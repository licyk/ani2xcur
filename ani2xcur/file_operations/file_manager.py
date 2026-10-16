"""文件操作工具"""

import os
import stat
import shutil
from pathlib import Path

from tqdm import tqdm

from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_LEVEL,
    LOGGER_COLOR,
    LOGGER_NAME,
)

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def remove_files(
    path: Path,
) -> None:
    """文件删除工具，支持删除只读文件和非空文件夹。

    Args:
        path (Path): 要删除的文件或目录路径
    Raises:
        ValueError: 路径不存在时
        OSError: 删除过程中的系统错误
    """

    if not _path_exists(path):
        logger.error("路径不存在: '%s'", path)
        raise ValueError(f"要删除的 {path} 路径不存在")

    def _handle_remove_readonly(
        func,
        path_str,
        _,
    ):
        """处理只读文件的错误处理函数"""
        if os.path.exists(path_str):
            os.chmod(path_str, stat.S_IWRITE)
            func(path_str)

    try:
        if path.is_symlink():
            # 处理符号链接, 不跟随链接修改目标权限
            logger.debug("删除软链接: '%s'", path)
            path.unlink()

        elif path.is_file():
            # 处理文件
            logger.debug("删除文件: '%s'", path)
            os.chmod(path, stat.S_IWRITE)
            path.unlink()

        elif path.is_dir():
            # 处理文件夹
            logger.debug("删除目录: '%s'", path)
            shutil.rmtree(path, onerror=_handle_remove_readonly)

    except OSError as e:
        logger.error("删除失败: '%s' - 原因: %s", path, e)
        raise e


def _path_exists(
    path: Path,
) -> bool:
    """判断路径是否存在, 包括失效软链接"""
    return path.exists() or path.is_symlink()


def _copy_symlink(
    src: Path,
    dst: Path,
) -> None:
    """复制软链接本身, 不复制软链接指向的内容"""
    if dst.exists() and dst.is_dir() and not dst.is_symlink():
        raise IsADirectoryError(f"目标路径已存在且为目录: {dst}")

    if _path_exists(dst):
        remove_files(dst)

    dst.symlink_to(os.readlink(src), target_is_directory=src.is_dir())


def copy_files(
    src: Path,
    dst: Path,
) -> None:
    """复制文件或目录

    Args:
        src (Path): 源文件路径
        dst (Path): 复制文件到指定的路径
    Raises:
        PermissionError: 没有权限复制文件时
        OSError: 复制文件失败时
        FileNotFoundError: 源文件未找到时
        ValueError: 路径逻辑错误（如循环复制）时
    """
    try:
        # 保留软链接路径本身, 只在循环检测时解析真实路径
        src_path = src.absolute()
        dst_path = dst.absolute()

        # 检查源是否存在
        if not _path_exists(src_path):
            logger.error("源路径不存在: '%s'", src)
            raise FileNotFoundError(f"源路径不存在: {src}")

        # 防止递归复制（例如将目录复制到其自身的子目录中）
        if src_path.is_dir() and not src_path.is_symlink() and dst_path.resolve().is_relative_to(src_path.resolve()):
            logger.error("不能将目录复制到自身或其子目录中: '%s'", src)
            raise ValueError(f"不能将目录复制到自身或其子目录中: {src}")

        # 如果目标是已存在的目录, 则在其下创建同名项
        if dst_path.exists() and dst_path.is_dir():
            dst_file = dst_path / src_path.name
        else:
            dst_file = dst_path

        # 确保目标父目录存在
        dst_file.parent.mkdir(parents=True, exist_ok=True)

        # 复制操作
        if src_path.is_symlink():
            _copy_symlink(src_path, dst_file)
        elif src_path.is_file():
            # copy2 会尽量保留文件元数据
            logger.debug("复制文件: '%s' -> '%s'", src_path, dst_file)
            shutil.copy2(src_path, dst_file)
        else:
            # symlinks=True: 保留软链接本身而非复制指向的内容
            # dirs_exist_ok=True: 实现合并逻辑，如果目标目录已存在则覆盖同名文件
            logger.debug("复制目录: '%s' -> '%s'", src_path, dst_file)
            try:
                shutil.copytree(src_path, dst_file, symlinks=True, dirs_exist_ok=True)
            except shutil.Error:
                # Linux 中遇到已存在的软链接会导致失败, 则使用 symlinks=False 重试
                logger.debug("保留软链接复制目录失败, 改为复制软链接目标内容: '%s' -> '%s'", src_path, dst_file)
                shutil.copytree(src_path, dst_file, symlinks=False, dirs_exist_ok=True)

    except PermissionError as e:
        logger.error("权限错误, 请检查文件权限或以管理员身份运行: %s", e)
        raise e
    except OSError as e:
        logger.error("复制失败: %s", e)
        raise e


def copy_files_merge(
    src: Path,
    dst: Path,
) -> None:
    """复制文件或目录, 当源为目录时直接合并到目标目录

    与 copy_files 的区别:
    当源路径为目录时, 不会在目标目录下额外创建源目录同名文件夹, 而是
    将源目录中的内容直接复制并合并到目标路径。

    Args:
        src (Path): 源文件路径
        dst (Path): 复制文件到指定的路径
    Raises:
        PermissionError: 没有权限复制文件时
        OSError: 复制文件失败时
        FileNotFoundError: 源文件未找到时
        ValueError: 路径逻辑错误（如循环复制）时
    """
    try:
        src_path = src.absolute()
        dst_path = dst.absolute()

        if not _path_exists(src_path):
            logger.error("源路径不存在: '%s'", src)
            raise FileNotFoundError(f"源路径不存在: {src}")

        if src_path.is_dir() and not src_path.is_symlink():
            if src_path.resolve() == dst_path.resolve():
                return

            if dst_path.resolve().is_relative_to(src_path.resolve()):
                logger.error("不能将目录复制到自身的子目录中: '%s'", src)
                raise ValueError(f"不能将目录复制到自身的子目录中: {src}")

            dst_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copytree(src_path, dst_path, symlinks=True, dirs_exist_ok=True)
            except shutil.Error:
                shutil.copytree(src_path, dst_path, symlinks=False, dirs_exist_ok=True)
            return

        if src_path == dst_path:
            return

        if dst_path.exists() and dst_path.is_dir():
            dst_file = dst_path / src_path.name
        else:
            dst_file = dst_path

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        if src_path.is_symlink():
            _copy_symlink(src_path, dst_file)
        else:
            shutil.copy2(src_path, dst_file)

    except PermissionError as e:
        logger.error("权限错误, 请检查文件权限或以管理员身份运行: %s", e)
        raise e
    except OSError as e:
        logger.error("复制失败: %s", e)
        raise e


def move_files(
    src: Path,
    dst: Path,
) -> None:
    """移动文件或目录

    Args:
        src (Path): 源路径
        dst (Path): 目标路径
    Raises:
        FileNotFoundError: 源路径不存在时
        PermissionError: 权限不足以移动文件时
        OSError: 移动文件失败时
        ValueError: 路径逻辑错误（如循环移动）时
    """
    try:
        src_path = src.absolute()
        dst_path = dst.absolute()

        if not _path_exists(src_path):
            logger.error("源路径不存在: '%s'", src)
            raise FileNotFoundError(f"源路径不存在: {src}")

        if src_path == dst_path:
            return

        # 确定目的路径
        if dst_path.exists() and dst_path.is_dir():
            final_dst = dst_path / src_path.name
        else:
            final_dst = dst_path

        if src_path.is_file() or src_path.is_symlink():
            if final_dst.is_file() or final_dst.is_symlink():
                remove_files(final_dst)

            final_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(final_dst))
            return

        if src_path.is_dir():
            src_real = src_path.resolve()
            final_dst_real = final_dst.resolve()
            if final_dst_real.is_relative_to(src_real):
                logger.error("不能将目录移动到自身或其子目录中: '%s'", src)
                raise ValueError(f"不能将目录移动到自身或其子目录中: {src}")

            if not final_dst.exists():
                final_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_path), str(final_dst))
            elif not final_dst.is_dir():
                remove_files(final_dst)
                shutil.move(str(src_path), str(final_dst))
            else:
                logger.debug("目标目录已存在，执行合并操作: '%s' -> '%s'", src_path, final_dst)
                for item in src_path.iterdir():
                    move_files(item, final_dst / item.name)

                if src_path.exists():
                    src_path.rmdir()

    except PermissionError as e:
        logger.error("权限错误, 请检查文件权限或以管理员身份运行: %s", e)
        raise e
    except OSError as e:
        logger.error("移动失败: %s", e)
        raise e


def move_files_merge(
    src: Path,
    dst: Path,
) -> None:
    """移动文件或目录, 当源为目录时直接合并到目标目录

    与 move_files 的区别:
    当源路径为目录时, 不会在目标目录下额外创建源目录同名文件夹, 而是
    将源目录中的内容直接移动并合并到目标路径。

    Args:
        src (Path): 源路径
        dst (Path): 目标路径
    Raises:
        FileNotFoundError: 源路径不存在时
        PermissionError: 权限不足以移动文件时
        OSError: 移动文件失败时
        ValueError: 路径逻辑错误（如循环移动）时
    """
    try:
        src_path = src.absolute()
        dst_path = dst.absolute()

        if not _path_exists(src_path):
            logger.error("源路径不存在: '%s'", src)
            raise FileNotFoundError(f"源路径不存在: {src}")

        if src_path == dst_path:
            return

        if src_path.is_file() or src_path.is_symlink():
            if dst_path.exists() and dst_path.is_dir():
                final_dst = dst_path / src_path.name
            else:
                final_dst = dst_path

            if final_dst.is_file() or final_dst.is_symlink():
                remove_files(final_dst)

            final_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(final_dst))
            return

        if src_path.is_dir():
            if dst_path.resolve().is_relative_to(src_path.resolve()):
                logger.error("不能将目录移动到自身的子目录中: '%s'", src)
                raise ValueError(f"不能将目录移动到自身的子目录中: {src}")

            if dst_path.exists() and not dst_path.is_dir():
                remove_files(dst_path)

            dst_path.mkdir(parents=True, exist_ok=True)
            logger.debug("目标目录执行直接合并操作: '%s' -> '%s'", src_path, dst_path)
            for item in src_path.iterdir():
                if item.is_symlink():
                    final_dst = dst_path / item.name
                    if final_dst.exists() or final_dst.is_symlink():
                        remove_files(final_dst)
                    final_dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(final_dst))
                else:
                    move_files_merge(item, dst_path / item.name)

            if src_path.exists():
                src_path.rmdir()

    except PermissionError as e:
        logger.error("权限错误, 请检查文件权限或以管理员身份运行: %s", e)
        raise e
    except OSError as e:
        logger.error("移动失败: %s", e)
        raise e


def get_file_list(
    path: Path,
    resolve: bool = False,
    max_depth: int = -1,
    show_progress: bool = True,
    include_dirs: bool = False,
) -> list[Path]:
    """获取当前路径下的所有文件和可选目录的绝对路径

    Args:
        path (Path): 要获取列表的目录
        resolve (bool): 是否完全解析路径, 包括链接路径
        max_depth (int): 最大遍历深度, -1 表示不限制深度, 0 表示只遍历当前目录
        show_progress (bool): 是否显示 tqdm 进度条
        include_dirs (bool): 是否在结果中包含目录路径
    Returns:
        list[Path]: 路径列表的绝对路径
    """

    if not path or not path.exists():
        logger.debug("获取文件列表时路径不存在: '%s'", path)
        return []

    if path.is_file():
        logger.debug("获取文件列表时输入为文件: '%s'", path)
        return [path.resolve() if resolve else path.absolute()]

    base_depth = len(path.resolve().parts)

    file_list: list[Path] = []
    with tqdm(desc=f"扫描目录 {path}", position=0, leave=True, disable=not show_progress) as dir_pbar:
        with tqdm(desc="发现条目数", position=1, leave=True, disable=not show_progress) as file_pbar:
            for root, dirs, files in os.walk(path):
                root_path = Path(root)
                current_depth = len(root_path.resolve().parts) - base_depth

                # 超过最大深度则阻止继续向下遍历
                if max_depth != -1 and current_depth >= max_depth:
                    # 如果需要包含目录, 虽然停止深挖, 但当前层的目录仍可加入
                    if include_dirs:
                        for d in dirs:
                            dir_path = root_path / d
                            file_list.append(dir_path.resolve() if resolve else dir_path.absolute())
                            file_pbar.update(1)
                    dirs.clear()
                else:
                    # 如果启用，将当前层级的目录加入列表
                    if include_dirs:
                        for d in dirs:
                            dir_path = root_path / d
                            file_list.append(dir_path.resolve() if resolve else dir_path.absolute())
                            file_pbar.update(1)

                for file in files:
                    file_path = root_path / file
                    file_list.append(file_path.resolve() if resolve else file_path.absolute())
                    file_pbar.update(1)

                dir_pbar.update(1)

    logger.debug("获取文件列表完成: path='%s', count=%s, include_dirs=%s, max_depth=%s", path, len(file_list), include_dirs, max_depth)
    return file_list


def save_create_symlink(
    target: Path,
    link: Path,
) -> None:
    """创建软链接, 当创建软链接失败时则尝试复制文件

    Args:
        target (Path): 源文件路径
        link (Path): 软链接到的目的路径
    """
    try:
        link.symlink_to(target)
        logger.debug("创建软链接: '%s' -> '%s'", target, link)
    except OSError:
        logger.debug("尝试创建软链接失败, 尝试复制文件: '%s' -> '%s'", target, link)
        copy_files(target, link)


def safe_is_file(
    path: Path,
) -> bool:
    """检查文件是否存在 (忽略大小写)

    Args:
        path (Path): 文件路径

    Returns:
        bool: 当文件存在时则返回 True
    """
    # 首先尝试原生检查 (性能最高)
    if path.is_file():
        return True

    # 如果原生检查失败 (可能是 Linux 大小写问题), 进行模糊查找
    parent = path.parent
    if not parent.is_dir():
        return False

    target_name = path.name.lower()
    # 遍历当前目录, 比对小写后的文件名
    for child in parent.iterdir():
        if child.name.lower() == target_name and child.is_file():
            return True

    return False


def get_real_path(
    path: Path,
) -> Path:
    """如果文件存在 (不计大小写), 返回文件系统中的真实路径, 否则返回原路径

    Args:
        path (Path): 原始文件路径

    Returns:
        Path: 文件系统中的真实路径
    """
    parent = path.parent
    target = path.name.lower()

    if not parent.exists():
        return path

    for child in parent.iterdir():
        if child.name.lower() == target:
            return child  # 返回 Linux 硬盘上真实的 Test1.ani
    return path
