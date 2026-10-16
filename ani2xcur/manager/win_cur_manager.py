"""Windows 鼠标指针管理工具"""

from typing import TypedDict
from pathlib import Path

from ani2xcur.config_parse.win import parse_inf_file_content
from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_LEVEL,
    LOGGER_COLOR,
    LOGGER_NAME,
)
from ani2xcur.file_operations.file_manager import (
    remove_files,
    copy_files,
    get_real_path,
)
from ani2xcur.config_parse.win import dict_to_inf_strings_format
from ani2xcur.manager.base import (
    CURSOR_KEYS,
    CurrentCursorInfoList,
    CursorMap,
    CursorSchemesList,
)
from ani2xcur.manager.desktop_config.base import check_windows_cursor_size_value
from ani2xcur.manager.desktop_config.windows import (
    WINDOWS_CURSOR_CURSORS_SCHEME_PATH,
    get_windows_cursor_size,
    get_windows_cursor_theme,
    has_var_string,
)
from ani2xcur.manager.desktop_config.windows import (
    set_windows_cursor_theme as apply_windows_cursor_theme,
)
from ani2xcur.manager.desktop_config.windows import (
    set_windows_cursor_size as apply_windows_cursor_size,
)
from ani2xcur.manager.regedit import (
    RegistryAccess,
    RegistryRootKey,
    RegistryValueType,
    registry_enum_values,
    registry_delete_value,
    registry_set_value,
    registry_query_value,
)
from ani2xcur.utils import extend_list_to_length
from ani2xcur.manager.desktop_config.windows import expand_var_string

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


class InstallWindowsSchemeInfo(TypedDict):
    """Windows 鼠标指针安装信息"""

    scheme_name: str
    """鼠标指针名称"""

    cursor_paths: list[Path]
    """鼠标指针文件列表"""

    default_reg: str
    """默认安装到注册表的鼠标指针方案, 使用 [Scheme.Reg] 中的值"""

    default_dst_cursor_paths: list[Path]
    """默认复制到的目的路径的鼠标指针文件列表"""

    vars_dict: dict[str, str]
    """INF 文件中的变量表"""

    cursor_map: CursorMap
    """鼠标指针类型与对应的路径地图"""


class WindowsCursorSchemeConfig(TypedDict):
    """Windows 鼠标指针导出配置"""

    cursor_src_file: list[Path]
    destination_dirs: str
    wreg: str
    scheme_reg: str
    scheme_cur: str
    strings: str


def extract_scheme_info_from_inf(
    inf_file: Path,
) -> InstallWindowsSchemeInfo:
    """从 INF 文件中获取鼠标指针配置

    Args:
        inf_file (Path): INF 文件路径
    Returns:
        InstallWindowsSchemeInfo: 鼠标指针安装配置
    Raises:
        ValueError: 鼠标指针配置文件中的注册表信息不合法时
    """

    def _expand_path(
        x: str,
    ) -> Path:
        return Path(expand_var_string(x.replace('"', "").replace("'", ""), vars_dict))

    cursor_map: CursorMap = {}
    inf_file_content = parse_inf_file_content(inf_file)
    scheme_reg = parse_scheme_reg_string(inf_file_content["SchemeReg"][0])
    vars_dict = inf_file_content["Strings"]
    scheme_name = vars_dict["SCHEME_NAME"]
    cursor_files = inf_file_content["CursorFiles"]

    # 检查 [Scheme.Reg] 长度合法性
    if len(scheme_reg) != 5:
        raise ValueError(f"鼠标指针配置中的注册表配置不合法, 配置长度: {len(scheme_reg)}")

    # 将鼠标指针字段扩展到合适长度
    cursor_reg_paths: list[str] = extend_list_to_length(scheme_reg[4].split(","), target_length=len(CURSOR_KEYS["win"]))

    # 检查 [Scheme.Reg] 中鼠标指针数量
    if len(cursor_reg_paths) > len(CURSOR_KEYS["win"]):
        raise ValueError(f"鼠标指针配置中指定的鼠标指针数量不合法, 指定的鼠标指针数量: {len(cursor_reg_paths)}")

    # 重新生成 [Scheme.Reg] 字段
    default_reg = generate_scheme_reg_string(
        key=scheme_reg[0],
        sub_key=scheme_reg[1],
        value_name=scheme_reg[2],
        dtype=scheme_reg[3],
        value=",".join(cursor_reg_paths),
    )

    # 统一路径分隔符 (Linux 中无法处理正确 `\` 路径分隔符字符串)
    cursor_reg_paths = [x.replace(r"\\", "/").replace("\\", "/") for x in cursor_reg_paths]
    logger.debug("统一后的注册表路径列表: %s", cursor_reg_paths)

    # 获取鼠标指针配置中指针文件的实际安装路径列表
    # 为什么要大小写不敏感啊, 呜呜呜
    default_dst_cursor_paths: list[Path] = []
    for x in cursor_reg_paths:
        logger.debug("尝试查找对应的鼠标指针文件: '%s'", x)
        p = get_real_path(_expand_path(x))
        if p.is_file():
            logger.debug("匹配到鼠标指针文件: '%s'", p)
            default_dst_cursor_paths.append(p)
            continue

    # 记录鼠标指针原文件路径和安装到的实际路径, 并记录成字典
    for key, value in zip(CURSOR_KEYS["win"], cursor_reg_paths):
        if value.strip() != "":
            dst_path = _expand_path(value)
            src_path = get_real_path(inf_file.parent / dst_path.name)  # 大小写不敏感好坑
            if not src_path.is_file():
                src_path = None
        else:
            dst_path = None
            src_path = None

        cursor_map[key] = {
            "dst_path": dst_path,
            "src_path": src_path,
        }

    # 鼠标指针原文件列表
    cursor_paths = [inf_file.parent / x for x in cursor_files if (inf_file.parent / x).is_file()]

    return {
        "scheme_name": scheme_name,
        "cursor_paths": cursor_paths,
        "default_reg": default_reg,
        "vars_dict": vars_dict,
        "default_dst_cursor_paths": default_dst_cursor_paths,
        "cursor_map": cursor_map,
    }


def parse_scheme_reg_string(
    scheme_reg_string: str,
) -> list[str]:
    """解析 INF 字符串中 [Scheme.Reg] 格式的字符串, 将字符串分割成列表

    Args:
        scheme_reg_string (str): 需要解析的字符串

    Returns:
        list[str]: 解析后的字符串列表
    """
    result: list[str] = []
    current = ""
    in_single_quotes = False
    in_double_quotes = False
    i = 0

    while i < len(scheme_reg_string):
        char = scheme_reg_string[i]

        if char == '"' and not in_single_quotes:
            # 切换双引号状态 (仅当不在单引号内)
            in_double_quotes = not in_double_quotes
            i += 1
        elif char == "'" and not in_double_quotes:
            # 切换单引号状态 (仅当不在双引号内)
            in_single_quotes = not in_single_quotes
            i += 1
        elif char == "," and not in_single_quotes and not in_double_quotes:
            # 只有在非引号状态下遇到逗号才分割
            result.append(current)
            current = ""
            i += 1
        else:
            # 添加字符到当前项
            current += char
            i += 1

    # 添加最后一项
    if current or scheme_reg_string.endswith(","):
        result.append(current)

    # 去除每项首尾的引号 (如果存在)
    cleaned_result: list[str] = []
    for item in result:
        cleaned_item = item
        # 如果同时以单引号开头结尾, 则去除单引号
        if len(cleaned_item) >= 2 and cleaned_item.startswith("'") and cleaned_item.endswith("'"):
            cleaned_item = cleaned_item[1:-1]
        # 如果同时以双引号开头结尾, 则去除双引号
        elif len(cleaned_item) >= 2 and cleaned_item.startswith('"') and cleaned_item.endswith('"'):
            cleaned_item = cleaned_item[1:-1]
        cleaned_result.append(cleaned_item)

    return cleaned_result


def generate_scheme_reg_string(
    key: str,
    sub_key: str,
    value_name: str,
    dtype: str,
    value: str,
) -> str:
    """生成 INF 字符串中 [Scheme.Reg] 格式的字符串

    [Scheme.Reg] 用于创建 Windows 注册表值, 格式: `<注册表根键>,<注册表子路径>,<键名>,<数据类型>,<值>`

    Args:
        key (str): 注册表根键
        sub_key (str): 注册表子路径
        value_name (str): 键名
        dtype (str): 数据类型
        value (str): 值
    Returns:
        str: [Scheme.Reg] 格式的字符串
    """
    return f'{key},"{sub_key}","{value_name}",{dtype},"{value}"'


def list_windows_cursors() -> CursorSchemesList:
    """列出 Windows 系统中已有的鼠标指针

    Returns:
        CursorSchemesList: 本地已安装的鼠标指针列表
    """
    schemes = registry_enum_values(
        sub_key=WINDOWS_CURSOR_CURSORS_SCHEME_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.READ,
    )
    cursors_list: CursorSchemesList = []
    for name, data in schemes.items():
        if not isinstance(data, str):
            continue
        cursor_files = [Path(expand_var_string(x)) for x in data.split(",") if x.strip() != "" and Path(expand_var_string(x)).is_file()]
        install_paths = list({x.parent for x in cursor_files})
        cursors_list.append(
            {
                "name": name,
                "cursor_files": cursor_files,
                "install_paths": install_paths,
            }
        )

    return cursors_list


def set_windows_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 Windows 桌面当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    Raises:
        ValueError: 鼠标指针不存在时
    """
    cursors = [x["name"] for x in list_windows_cursors()]
    if cursor_name not in cursors:
        logger.error("鼠标指针 '%s 不存在", cursor_name)
        raise ValueError(f"鼠标指针 {cursor_name} 不存在")

    logger.info("将 Windows 系统中使用的鼠标指针主题设置为 '%s'", cursor_name)
    apply_windows_cursor_theme(cursor_name)
    logger.info("Windows 鼠标指针主题已设置为 '%s'", cursor_name)


def set_windows_cursor_size(
    cursor_size: int,
) -> None:
    """设置 Windows 桌面当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    Raises:
        TypeError: 鼠标指针大小的值不是整数时
        ValueError: 鼠标指针大小的值超过合法范围时
    """
    try:
        check_windows_cursor_size_value(cursor_size)
    except TypeError as e:
        raise TypeError("鼠标指针大小的值必须为整数") from e
    except ValueError as e:
        raise ValueError("鼠标指针大小的值超过合法范围") from e
    logger.info("将 Windows 系统中使用的鼠标指针大小设置为 %s", cursor_size)
    apply_windows_cursor_size(cursor_size)
    logger.info("鼠标指针大小已设置为 %s", cursor_size)


def get_windows_cursor_info() -> CurrentCursorInfoList:
    """获取 Windows 当前鼠标指针信息

    Returns:
        CurrentCursorInfoList: 桌面平台的当前鼠标指针信息列表
    """
    logger.info("获取 Windows 系统的鼠标指针状态")
    return [
        {
            "platform": "Windows",
            "cursor_name": get_windows_cursor_theme(),
            "cursor_size": get_windows_cursor_size(),
        }
    ]


def delete_windows_cursor(
    cursor_name: str,
) -> None:
    """删除 Windows 系统上指定的鼠标指针

    Args:
        cursor_name (str): 要删除的鼠标指针名称
    Raises:
        RuntimeError: 删除鼠标指针文件失败时
        ValueError: 指定的鼠标指针不存在或者正在被使用时
    """
    cursors = list_windows_cursors()
    if cursor_name not in [x["name"] for x in cursors]:
        raise ValueError(f"鼠标指针 {cursor_name} 不存在")

    if cursor_name == get_windows_cursor_theme():
        raise ValueError(f"鼠标指针 {cursor_name} 正在被使用, 无法删除")

    logger.info("从 Windows 系统删除 '%s' 鼠标指针中", cursor_name)

    # 统计需要删除和保留的鼠标指针文件
    delete_file_paths: list[Path] = []
    preserve_file_paths: list[Path] = []
    delete_parent_paths: list[Path] = []
    for scheme in cursors:
        if cursor_name == scheme["name"]:
            delete_file_paths += scheme["cursor_files"]
            delete_parent_paths += scheme["install_paths"]
        else:
            preserve_file_paths += scheme["cursor_files"]

    # 计算需要删除的文件
    preserve_file_paths_set = set(preserve_file_paths)
    need_delete_file_paths = [x for x in delete_file_paths if x not in preserve_file_paths_set]

    logger.debug("%s 所属的鼠标指针文件列表: %s", cursor_name, delete_file_paths)
    logger.debug("%s 所属的鼠标指针安装目录列表: %s", cursor_name, delete_parent_paths)
    logger.debug("%s 需要删除的鼠标指针文件列表: %s", cursor_name, need_delete_file_paths)

    # 清理鼠标指针文件
    for file in need_delete_file_paths:
        try:
            logger.debug("清理鼠标指针文件 '%s'", file)
            remove_files(file)
        except OSError as e:
            logger.error(
                "删除 '%s' 鼠标指针所使用的指针文件 '%s' 发生错误: %s\n可尝试使用管理员权限运行 Ani2xcur 进行删除, 或者尝试手动删除文件",
                cursor_name,
                file,
                e,
            )
            raise RuntimeError(f"删除 {cursor_name} 鼠标指针所使用的指针文件 {file} 发生错误: {e}\n可尝试使用管理员权限运行 Ani2xcur 进行删除, 或者尝试手动删除文件") from e

    # 清理鼠标指针的父文件夹
    for file in delete_parent_paths:
        if not file.is_dir():
            logger.debug("鼠标指针文件的父文件夹 '%s' 不存在", file)
            continue

        if any(file.iterdir()):
            logger.debug("鼠标指针文件的父文件夹 '%s' 不为空, 跳过清理", file)
            continue

        try:
            logger.debug("清理鼠标指针文件的父文件夹 '%s'", file)
            remove_files(file)
        except OSError as e:
            logger.error(
                "清理 '%s' 鼠标指针文件的残留文件夹 '%s' 发生错误: %s\n可尝试使用管理员权限运行 Ani2xcur 进行删除, 或者尝试手动删除文件",
                cursor_name,
                file,
                e,
            )
            raise RuntimeError(f"清理 {cursor_name} 鼠标指针文件的残留文件夹 {file} 发生错误: {e}\n可尝试使用管理员权限运行 Ani2xcur 进行删除, 或者尝试手动删除文件") from e

    # 清理注册表中对应的鼠标指针方案
    registry_delete_value(
        name=cursor_name,
        sub_key=WINDOWS_CURSOR_CURSORS_SCHEME_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.SET_VALUE,
    )

    logger.info("从 Windows 系统删除 '%s' 鼠标指针完成", cursor_name)


def install_windows_cursor(
    inf_file: Path,
    cursor_install_path: Path | None = None,
) -> None:
    """通过 INF 配置文件安装鼠标指针

    Args:
        inf_file (Path): 鼠标指针配置文件路径
        cursor_install_path (Path | None): 自定义鼠标指针文件安装路径, 当为 None 时使用 INF 配置文件中的路径
    Raises:
        PermissionError: 复制鼠标指针文件时没有权限时
    """
    scheme_info = extract_scheme_info_from_inf(inf_file)
    copy_paths: list[tuple[Path, Path]] = []
    cursor_paths_in_reg: list[str] = []
    cursor_name = scheme_info["scheme_name"]
    install_path = None

    # 生成复制路径列表
    if cursor_install_path is not None:
        # 使用自定义安装路径
        install_path = cursor_install_path
        for _, cursor_pair in scheme_info["cursor_map"].items():
            src = cursor_pair["src_path"]
            dst_path = cursor_pair["dst_path"]
            if src is not None and dst_path is not None:
                dst = cursor_install_path / cursor_name / dst_path.name
                cursor_paths_in_reg.append(str(dst))
                copy_paths.append((src, dst))
            else:
                cursor_paths_in_reg.append("")

        # 生成需要写入注册表的方案对应值
        reg_scheme_value = ",".join(cursor_paths_in_reg)
    else:
        for _, cursor_pair in scheme_info["cursor_map"].items():
            src = cursor_pair["src_path"]
            dst_path = cursor_pair["dst_path"]
            if src is not None and dst_path is not None:
                install_path = dst_path.parent
                copy_paths.append((src, dst_path))

        # 生成需要写入注册表的方案对应值, 使用原始值
        reg_scheme_value = parse_scheme_reg_string(scheme_info["default_reg"])[4]

    logger.info("将 '%s' 鼠标指针安装到 '%s' 中", cursor_name, install_path)

    # 复制鼠标指针文件
    for src, dst in copy_paths:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            copy_files(src, dst)
        except OSError as e:
            logger.error(
                "复制 '%s' 到 '%s' 时发送错误: %s\n可尝试使用管理员权限运行 Ani2xcur",
                src,
                dst,
                e,
            )
            raise PermissionError(f"复制 {src} 到 {dst} 时发送错误: {e}\n可尝试使用管理员权限运行 Ani2xcur, 再执行鼠标指针安装操作") from e

    # 将方案写入注册表
    reg_type = RegistryValueType.EXPAND_SZ if has_var_string(reg_scheme_value) else RegistryValueType.SZ
    registry_set_value(
        name=cursor_name,
        value=reg_scheme_value,
        reg_type=reg_type,
        sub_key=WINDOWS_CURSOR_CURSORS_SCHEME_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.SET_VALUE,
    )
    logger.info("'%s' 鼠标指针已安装到 Windows 系统中", cursor_name)


def export_windows_cursor(
    cursor_name: str,
    output_path: Path,
    custom_install_path: Path | None = None,
) -> Path:
    """将系统中指定的鼠标指针方案导出为文件

    Args:
        cursor_name (str): 要导出的鼠标指针方案的名称
        output_path (Path): 鼠标指针导出的路径
        custom_install_path (Path | None): 自定义鼠标指针安装时的文件安装路径
    Returns:
        Path: 鼠标指针导出的文件路径
    Raises:
        ValueError: 鼠标指针在当前环境中不存在时
    """
    cursors = list_windows_cursors()
    cursor_data = None
    for data in cursors:
        if data["name"] == cursor_name:
            cursor_data = data

    if cursor_data is None:
        raise ValueError(f"鼠标指针 {cursor_name} 不存在")

    config_dict = generate_cursor_scheme_config(
        cursor_name=cursor_name,
        custom_install_path=custom_install_path,
    )

    reg_content = generate_cursor_scheme_inf_string(
        destination_dirs=config_dict["destination_dirs"],
        wreg=config_dict["wreg"],
        scheme_reg=config_dict["scheme_reg"],
        scheme_cur=config_dict["scheme_cur"],
        strings=config_dict["strings"],
    )

    save_dir = output_path / cursor_name
    save_dir.mkdir(parents=True, exist_ok=True)
    inf_file_path = save_dir / "AutoSetup.inf"
    logger.info("将 '%s' 鼠标指针导出到 '%s' 中", cursor_name, save_dir)
    for cursor in config_dict["cursor_src_file"]:
        copy_files(cursor, save_dir)

    # Windows 系统只能使用 GBK 编码保存 INF
    with open(inf_file_path, "w", encoding="gbk") as file:
        file.write(reg_content)

    logger.info("'%s' 鼠标指针导出到 '%s' 完成", cursor_name, save_dir)
    return save_dir


def generate_cursor_scheme_inf_string(
    destination_dirs: str,
    wreg: str,
    scheme_reg: str,
    scheme_cur: str,
    strings: str,
) -> str:
    """生成鼠标指针安装配置文件

    Args:
        destination_dirs (str): [DestinationDirs] 字段
        wreg (str): [Wreg] 字段
        scheme_reg (str): [Scheme.Reg] 字段
        scheme_cur (str): [Scheme.Cur] 字段
        strings (str): [Strings] 字段
    Returns:
        str: 鼠标指针的 INF 字符串
    """
    inf_content = r"""
[Version]
signature="$CHICAGO$"


[DefaultInstall]
CopyFiles = Scheme.Cur
AddReg    = Scheme.Reg,Wreg


[DestinationDirs]
Scheme.Cur = {{DESTINATION_DIRS}}


[Scheme.Reg]
{{SCHEME_REG}}


[Wreg]
{{WREG}}


[Scheme.Cur]
{{SCHEME_CUR}}


[Strings]
{{STRING_VARS}}

""".strip()

    return (
        inf_content.replace(r"{{DESTINATION_DIRS}}", destination_dirs.strip())
        .replace(r"{{WREG}}", wreg.strip())
        .replace(r"{{SCHEME_REG}}", scheme_reg.strip())
        .replace(r"{{SCHEME_CUR}}", scheme_cur.strip())
        .replace(r"{{STRING_VARS}}", strings.strip())
    )


def generate_cursor_scheme_config(
    cursor_name: str,
    custom_install_path: Path | None = None,
) -> WindowsCursorSchemeConfig:
    """生成鼠标指针的配置字典

    配置字段包括 cursor_src_file、destination_dirs、wreg、scheme_reg、scheme_cur 和 strings。

    Args:
        cursor_name (str): 要导出的鼠标指针方案的名称
        custom_install_path (Path | None): 自定义鼠标指针安装路径
    Returns:
        WindowsCursorSchemeConfig: 鼠标指针的配置字典
    Raises:
        ValueError: 鼠标指针方案不存在或配置不完整时
    """

    # 查找鼠标指针对应的方案信息
    cursor_paths_in_reg = registry_query_value(
        name=cursor_name,
        sub_key=WINDOWS_CURSOR_CURSORS_SCHEME_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.READ,
    )

    if not isinstance(cursor_paths_in_reg, str):
        raise ValueError(f"鼠标指针 {cursor_name} 不存在或注册表数据格式不正确")

    cursor_paths: list[Path] = []  # 用于导出的路径列表
    paths_to_reg: list[str] = []  # [Scheme.Reg] 部分
    strings: dict[str, str] = {}  # [Strings] 部分
    wreg_list: list[str] = []  # [Wreg] 部分
    wreg_list.append(r'HKCU,"Control Panel\Cursors",,0x00020000,"%SCHEME_NAME%"')
    strings["SCHEME_NAME"] = cursor_name

    # 将路径字符串解释成实际鼠标指针文件路径
    raw_paths: list[str] = extend_list_to_length(cursor_paths_in_reg.split(","), target_length=len(CURSOR_KEYS["win"]))[: len(CURSOR_KEYS["win"])]
    for key, origin_path in zip(CURSOR_KEYS["win"], raw_paths):
        path = Path(expand_var_string(origin_path)) if origin_path.strip() != "" and Path(expand_var_string(origin_path)).is_file() else None
        if path is not None:
            cursor_paths.append(path)

        path_in_reg = ""
        if custom_install_path is not None and path is not None:
            # 使用自定义安装路径
            path_in_reg = str(custom_install_path / cursor_name / f"%{key}%")
        elif path is not None:
            # 使用默认安装路径
            path_in_reg = rf"%10%\%CUR_DIR%\%{key}%"

        paths_to_reg.append(path_in_reg)
        if path_in_reg != "" and path is not None:
            strings[key] = path.name
            wreg_list.append(rf'HKCU,"Control Panel\Cursors",{key},0x00020000,"{path_in_reg}"')

    wreg_list.append(r'HKLM,"SOFTWARE\Microsoft\Windows\CurrentVersion\Runonce\Setup\","",,"rundll32.exe shell32.dll,Control_RunDLL main.cpl @0"')
    wreg = "\n".join(wreg_list)

    # 配置 [DistinationDirs] 字段和部分 [Strings] 字段
    if custom_install_path is not None:
        # 使用自定义安装路径
        custom_path = str(custom_install_path / cursor_name)
        strings["CUR_DIR"] = custom_path
        destination_dirs = r'-1,"%CUR_DIR%"'
    else:
        strings["CUR_DIR"] = rf"Cursors\{cursor_name}"
        destination_dirs = r'10,"%CUR_DIR%"'

    # 配置 [Scheme.Reg] 字段
    paths_to_reg_string = ",".join(paths_to_reg)
    if custom_install_path is not None:
        scheme_reg = rf'HKCU,"Control Panel\Cursors\Schemes","%SCHEME_NAME%",,"{paths_to_reg_string}"'
    else:
        scheme_reg = rf'HKCU,"Control Panel\Cursors\Schemes","%SCHEME_NAME%",0x00020000,"{paths_to_reg_string}"'

    # 配置 [Scheme.Cur] 字段
    scheme_cur = "\n".join([f'"{x.name}"' for x in cursor_paths])

    return {
        "cursor_src_file": cursor_paths,
        "destination_dirs": destination_dirs,
        "wreg": wreg,
        "scheme_reg": scheme_reg,
        "scheme_cur": scheme_cur,
        "strings": dict_to_inf_strings_format(strings),
    }
