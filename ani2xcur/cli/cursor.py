"""系统鼠标指针管理工具"""

import sys
from typing import (
    Annotated,
    Any,
)
from pathlib import Path
from tempfile import TemporaryDirectory

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from ani2xcur.manager.base import (
    WINDOWS_USER_CURSOR_PATH,
    LINUX_USER_ICONS_PATH,
)
from ani2xcur.manager.win_cur_manager import (
    install_windows_cursor,
    delete_windows_cursor,
    export_windows_cursor,
    set_windows_cursor_theme,
    set_windows_cursor_size,
    list_windows_cursors,
    get_windows_cursor_info,
)
from ani2xcur.manager.linux_cur_manager import (
    install_linux_cursor,
    delete_linux_cursor,
    export_linux_cursor,
    set_linux_cursor_theme,
    set_linux_cursor_size,
    list_linux_cursors,
    get_linux_cursor_info,
)
from ani2xcur.config import (
    LOGGER_NAME,
    LOGGER_LEVEL,
    LOGGER_COLOR,
    SMART_FINDER_SEARCH_DEPTH,
)
from ani2xcur.logger import get_logger
from ani2xcur.smart_finder import (
    find_inf_file,
    find_desktop_entry_file,
)
from ani2xcur.file_operations.archive_manager import (
    ArchiveFormat,
    create_archive,
)

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def install_cursor(
    input_path: Annotated[
        str,
        typer.Argument(
            help="鼠标指针文件的本地路径或下载链接, 输入鼠标指针压缩包文件路径/链接, 或者: Windows 平台中输入 inf / ani / cur 文件路径; Linux 平台输入 index.theme 文件路径",
        ),
    ],
    install_path: Annotated[
        Path | None,
        typer.Option(
            help="自定义鼠标指针文件安装路径, 默认为鼠标指针配置文件中指定的安装路径",
            resolve_path=True,
        ),
    ] = None,
    use_inf_config_path: Annotated[
        bool,
        typer.Option(
            help="(仅 Windows 平台) 使用 INF 配置文件中的鼠标指针安装路径",
        ),
    ] = False,
) -> None:
    """将鼠标指针安装到系统中

    Args:
        input_path: 鼠标指针配置文件、光标文件、压缩包路径或下载链接
        install_path: 自定义鼠标指针安装路径
        use_inf_config_path: Windows 平台是否使用 INF 中的安装路径
    Raises:
        FileNotFoundError: 未找到鼠标指针配置文件或光标目录时
        NotImplementedError: 当前平台不支持安装鼠标指针时
        PermissionError: 当前权限不足时
        RuntimeError: 安装过程失败时
    """
    if sys.platform == "win32":
        if install_path is None:
            if use_inf_config_path:
                logger.info("使用 INF 配置文件中的鼠标指针安装路径")
            else:
                install_path = WINDOWS_USER_CURSOR_PATH
                logger.info("未指定鼠标指针安装路径, 使用默认鼠标指针安装路径: '%s'", install_path)
        else:
            logger.info("使用自定义鼠标指针安装路径: '%s'", install_path)

        logger.info("安装的 Windows 鼠标指针: '%s'", input_path)
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            inf_file = find_inf_file(
                input_file=input_path,
                temp_dir=temp_dir,
                depth=SMART_FINDER_SEARCH_DEPTH,
            )
            if inf_file is None:
                raise FileNotFoundError("未找到鼠标指针的 INF 配置文件路径, 该鼠标指针文件无法安装")

            try:
                install_windows_cursor(
                    inf_file=inf_file,
                    cursor_install_path=install_path,
                )
            except PermissionError as e:
                raise PermissionError(
                    f"在 Windows 系统上安装鼠标指针时发生错误: {e}\n请检查是否使用管理员权限运行 Ani2xcur 运行, 或者尝试使用 --install-path 参数指定其他鼠标指针的安装路径"
                ) from e
    elif sys.platform == "linux":
        if install_path is None:
            install_path = LINUX_USER_ICONS_PATH
            logger.info("未指定鼠标指针安装路径, 使用默认鼠标指针安装路径: '%s'", install_path)
        else:
            logger.info("使用自定义鼠标指针安装路径: '%s'", install_path)

        logger.info("安装的 Linux 鼠标指针: '%s'", input_path)
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            desktop_entry_file = find_desktop_entry_file(
                input_file=input_path,
                temp_dir=temp_dir,
                depth=SMART_FINDER_SEARCH_DEPTH,
            )

            if desktop_entry_file is None:
                raise FileNotFoundError("未找到鼠标指针的 DesktopEntry 配置文件路径")

            if not (desktop_entry_file.parent / "cursors").is_dir():
                raise FileNotFoundError("鼠标指针目录缺失, 无法进行鼠标指针转换")

            try:
                install_linux_cursor(
                    desktop_entry_file=desktop_entry_file,
                    cursor_install_path=install_path,
                )
            except (FileNotFoundError, RuntimeError) as e:
                raise RuntimeError(
                    "在 Linux 系统上安装鼠标指针时发生错误: "
                    f"{e}\n请检查是否有权限写入安装路径, 或者尝试使用 --install-path 参数指定其他鼠标指针的安装路径\n鼠标指针文件可能也出现损坏, 也请检查鼠标指针文件的完整性"
                ) from e
    else:
        raise NotImplementedError(f"不支持的系统: {sys.platform}")


def uninstall_cursor(
    cursor_name: Annotated[
        str,
        typer.Argument(
            help="要删除的鼠标指针名称",
        ),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="直接确认删除鼠标指针",
        ),
    ] = False,
) -> None:
    """删除系统中指定的鼠标指针

    Args:
        cursor_name: 要删除的鼠标指针名称
        force: 是否跳过确认提示
    Raises:
        NotImplementedError: 当前平台不支持删除鼠标指针时
        RuntimeError: 删除过程失败时
        ValueError: 鼠标指针不存在或正在使用时
    """
    if sys.platform == "win32":
        if not force:
            typer.confirm(f"确认删除 {cursor_name} 鼠标指针吗?", abort=True)

        try:
            delete_windows_cursor(cursor_name)
        except RuntimeError as e:
            raise RuntimeError(f"删除鼠标指针时发生错误: {e}\n可能为没有权限进行删除鼠标指针文件, 可尝试使用管理员权限运行 Ani2xcur") from e
        except ValueError as e:
            raise ValueError(f"删除鼠标指针时发生错误: {e}\n请检查要删除的鼠标指针是否存在或者正在使用") from e
    elif sys.platform == "linux":
        if not force:
            typer.confirm(f"确认删除 {cursor_name} 鼠标指针吗?", abort=True)

        try:
            delete_linux_cursor(cursor_name)
        except RuntimeError as e:
            raise RuntimeError(f"删除鼠标指针时发生错误: {e}\n可能为没有权限进行删除鼠标指针文件, 可尝试使用 root 权限运行 Ani2xcur") from e
        except ValueError as e:
            raise ValueError(f"删除鼠标指针时发生错误: {e}\n请检查要删除的鼠标指针是否存在") from e
    else:
        raise NotImplementedError(f"不支持的系统: {sys.platform}")


def export_cursor(
    cursor_name: Annotated[
        str,
        typer.Argument(
            help="要导出的鼠标指针名称",
        ),
    ],
    output_path: Annotated[
        Path,
        typer.Argument(
            help="鼠标指针的导出路径",
            resolve_path=True,
        ),
    ],
    custom_install_path: Annotated[
        Path | None,
        typer.Option(
            help="自定义鼠标指针配置文件在安装时的文件安装路径",
            resolve_path=True,
        ),
    ] = None,
    compress: Annotated[
        bool,
        typer.Option(
            help="导出完成后将鼠标指针打包成压缩包",
        ),
    ] = False,
    compress_format: Annotated[
        ArchiveFormat,
        typer.Option(
            help="打包成压缩包时使用的压缩包格式",
        ),
    ] = ".zip",
) -> None:
    """将鼠标指针从系统中导出

    Args:
        cursor_name: 要导出的鼠标指针名称
        output_path: 导出路径
        custom_install_path: 导出配置中记录的自定义安装路径
        compress: 是否在导出后打包
        compress_format: 压缩包格式
    Raises:
        NotImplementedError: 当前平台不支持导出鼠标指针时
        RuntimeError: 导出过程失败时
        ValueError: 鼠标指针不存在时
    """
    if sys.platform == "win32":
        try:
            path = export_windows_cursor(
                cursor_name=cursor_name,
                output_path=output_path,
                custom_install_path=custom_install_path,
            )
            logger.info("Windows 鼠标指针导出完成, 导出路径: '%s'", path)
            if compress:
                logger.info("将 Windows 鼠标指针进行打包")
                archive_path = output_path / f"{path.name}{compress_format}"
                create_archive(
                    sources=[path],
                    archive_path=archive_path,
                )
                logger.info("Windows 鼠标指针打包完成, 保存路径: '%s'", archive_path)
        except ValueError as e:
            raise ValueError(f"导出鼠标指针发生错误: {e}\n请检查导出的鼠标指针是否存在于系统中") from e
    elif sys.platform == "linux":
        try:
            path = export_linux_cursor(
                cursor_name=cursor_name,
                output_path=output_path,
                custom_install_path=custom_install_path,
            )
            logger.info("Linux 鼠标指针导出完成, 导出路径: '%s'", path)
            if compress:
                logger.info("将 Linux 鼠标指针进行打包")
                archive_path = output_path / f"{path.name}{compress_format}"
                create_archive(
                    sources=[path],
                    archive_path=archive_path,
                )
                logger.info("Linux 鼠标指针打包完成, 保存路径: '%s'", archive_path)
        except ValueError as e:
            raise ValueError(f"导出鼠标指针发生错误: {e}\n请检查导出的鼠标指针是否存在于系统中") from e
        except RuntimeError as e:
            raise RuntimeError(f"导出鼠标指针发生错误: {e}\n可能为导出路径无权限读写, 可尝试修改导出路径进行尝试, 或者使用 root 权限运行 Ani2xcur") from e
    else:
        raise NotImplementedError(f"不支持的系统: {sys.platform}")


def set_cursor_theme(
    cursor_name: Annotated[
        str,
        typer.Argument(
            help="要指定的鼠标指针名称",
        ),
    ],
) -> None:
    """设置系统要使用的鼠标指针主题

    Args:
        cursor_name: 要设置的鼠标指针主题名称
    Raises:
        NotImplementedError: 当前平台不支持设置鼠标指针主题时
        ValueError: 鼠标指针主题不存在时
    """
    if sys.platform == "win32":
        try:
            set_windows_cursor_theme(cursor_name)
        except ValueError as e:
            raise ValueError(f"设置鼠标指针主题时发生错误: {e}\n请检查要设置的鼠标指针主题是否安装到系统中") from e
    elif sys.platform == "linux":
        try:
            set_linux_cursor_theme(cursor_name)
        except ValueError as e:
            raise ValueError(f"设置鼠标指针主题时发生错误: {e}\n请检查要设置的鼠标指针主题是否安装到系统中") from e
    else:
        raise NotImplementedError(f"不支持的系统: {sys.platform}")


def set_cursor_size(
    cursor_size: Annotated[
        int,
        typer.Argument(
            help="要指定的鼠标指针大小",
        ),
    ],
) -> None:
    """设置系统要使用的鼠标指针大小

    Args:
        cursor_size: 要设置的鼠标指针大小
    Raises:
        NotImplementedError: 当前平台不支持设置鼠标指针大小时
        TypeError: 鼠标指针大小不是整数时
        ValueError: 鼠标指针大小超出合法范围时
    """
    if sys.platform == "win32":
        try:
            set_windows_cursor_size(cursor_size)
        except TypeError as e:
            raise TypeError(f"设置鼠标指针大小时发生错误: {e}\n请检查鼠标指针大小的是否为整数") from e
        except ValueError as e:
            raise ValueError(f"设置鼠标指针大小时发生错误: {e}\n请检查鼠标指针大小的值是否在合法范围") from e
    elif sys.platform == "linux":
        try:
            set_linux_cursor_size(cursor_size)
        except TypeError as e:
            raise TypeError(f"设置鼠标指针大小时发生错误: {e}\n请检查鼠标指针大小的是否为整数") from e
        except ValueError as e:
            raise ValueError(f"设置鼠标指针大小时发生错误: {e}\n请检查鼠标指针大小的值是否在合法范围") from e
    else:
        raise NotImplementedError(f"不支持的系统: {sys.platform}")


def list_cursor() -> None:
    """列出当前系统中已安装的鼠标指针

    Raises:
        NotImplementedError: 当前平台不支持列出鼠标指针时
    """

    def _display_frame(
        items: list[Any],
    ) -> None:
        console = Console()

        # 设置表格整体样式
        table = Table(
            header_style="bright_yellow",
            border_style="bright_black",
            box=box.ROUNDED,
        )

        # 设置列样式
        # style 参数控制该列所有单元格的默认样式
        table.add_column("鼠标指针名称", style="bold white", no_wrap=True)
        table.add_column("数量", justify="left", style="white")
        table.add_column("安装路径", style="cyan", overflow="fold")

        for item in items:
            path = ", ".join([str(x) for x in item["install_paths"]])
            count = len(item["cursor_files"])

            table.add_row(item["name"], str(count), path)

        console.print(table)

    if sys.platform == "win32":
        logger.info("获取 Windows 系统中已安装的鼠标指针列表")
        cursors = list_windows_cursors()
    elif sys.platform == "linux":
        logger.info("获取 Linux 系统中已安装的鼠标指针列表")
        cursors = list_linux_cursors()
    else:
        raise NotImplementedError(f"不支持的系统: {sys.platform}")

    _display_frame(cursors)


def get_current_cursor() -> None:
    """显示当前系统中设置的鼠标指针名称和大小

    Raises:
        NotImplementedError: 当前平台不支持读取鼠标指针信息时
    """

    def _display_frame(
        items: list[Any],
    ) -> None:
        console = Console()

        # 设置表格整体样式
        table = Table(
            header_style="bright_yellow",
            border_style="bright_black",
            box=box.ROUNDED,
        )

        # 设置列样式
        # style 参数控制该列所有单元格的默认样式
        table.add_column("平台", style="bold white", no_wrap=True)
        table.add_column("鼠标指针主题", justify="left", style="white")
        table.add_column("鼠标指针大小", style="cyan", overflow="fold")

        for item in items:
            platform = item["platform"]
            cursor_name = item["cursor_name"]
            cursor_size = item["cursor_size"]

            table.add_row(platform, str(cursor_name), str(cursor_size))

        console.print(table)

    if sys.platform == "win32":
        info = get_windows_cursor_info()
    elif sys.platform == "linux":
        info = get_linux_cursor_info()
    else:
        raise NotImplementedError(f"不支持的系统: {sys.platform}")

    _display_frame(info)
