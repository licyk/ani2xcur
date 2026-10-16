"""Windows 鼠标指针配置解析"""

from pathlib import Path
from typing import (
    TypedDict,
)

from ani2xcur.config_parse.parse import (
    ParsedINF,
    parse_inf_file,
)


CursorShemeINF = TypedDict(
    "CursorShemeINF",
    {
        "Version": dict[str, str | list[str]],  # 版本信息
        "DefaultInstall": dict[str, list[str]],  # 默认需要安装的配置
        "DestinationDirs": dict[str, str | list[str]],  # 目的路径
        "CopyFiles": dict[str, list[str]],  # CopyFiles 引用的真实复制节内容
        "AddReg": dict[str, list[str]],  # AddReg 引用的真实注册表节内容
        "CursorFiles": list[str],  # 最终用于转换/安装的光标文件名列表
        "CursorFilesSection": str,  # CursorFiles 来源节名
        "SchemeReg": list[str],  # 最终用于方案注册的注册表配置
        "SchemeRegSection": str,  # SchemeReg 来源节名
        "Strings": dict[str, str],  # 配置中使用的变量
    },
    total=False,
)
"""预处理后的鼠标指针配置 INF 结构"""


def _section_var(
    parsed: ParsedINF,
    section_name: str,
) -> dict[str, str | list[str]]:
    """获取指定节中的变量映射，并保留解析器返回的具体类型。"""
    return parsed[section_name].get("var", {})


def _section_constant(
    parsed: ParsedINF,
    section_name: str,
) -> list[str]:
    """获取指定节中的常量行列表，并保留解析器返回的具体类型。"""
    return parsed[section_name].get("constant", [])


def _required_section_var(
    parsed: ParsedINF,
    section_name: str,
) -> dict[str, str | list[str]]:
    if section_name not in parsed:
        raise ValueError(f"未找到 {section_name} 键, 鼠标指针配置不完整")
    return _section_var(parsed, section_name)


def _ensure_list(
    value: str | list[str],
) -> list[str]:
    return value if isinstance(value, list) else [value]


def _install_section_name(
    value: str,
) -> str | None:
    """从 CopyFiles/AddReg 条目中提取节名。"""
    name = value.strip().strip('"').strip("'")
    if not name or name.startswith("@"):
        return None
    return name


def _section_names_from_default_install(
    default_install: dict[str, list[str]],
    key: str,
) -> list[str]:
    section_names: list[str] = []
    for value in default_install.get(key, []):
        section_name = _install_section_name(value)
        if section_name is not None and section_name not in section_names:
            section_names.append(section_name)
    return section_names


def _looks_like_cursor_file_list(
    values: list[str],
) -> bool:
    return any(value.strip().strip('"').strip("'").lower().endswith((".ani", ".cur")) for value in values)


def _ensure_str_dict(
    data: dict[str, str | list[str]],
    section_name: str,
) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(value, str):
            raise ValueError(f"{section_name} 中的 {key} 必须为字符串")
        result[key] = value
    return result


def preprocess_inf_to_cursor_scheme(
    parsed: ParsedINF,
) -> CursorShemeINF:
    """将 ParsedINF 处理为鼠标指针安装需要的结构

    Version、DefaultInstall、DestinationDirs 和 Strings 为必需节。CopyFiles、
    AddReg 的真实节名来自 DefaultInstall，不再假设 Scheme.Cur、Scheme.Reg
    或 Wreg 等固定节名。

    Args:
        parsed (ParsedINF): INF 类型字典
    Returns:
        CursorShemeINF: 预处理后的鼠标指针 INF 信息字典
    Raises:
        ValueError: 当鼠标指针配置文件不完整时
    """

    out: CursorShemeINF = {}

    out["Version"] = _required_section_var(parsed, "Version")

    default_install: dict[str, list[str]] = {}
    for key, value in _required_section_var(parsed, "DefaultInstall").items():
        default_install[key] = _ensure_list(value)
    out["DefaultInstall"] = default_install

    out["DestinationDirs"] = _required_section_var(parsed, "DestinationDirs")
    out["Strings"] = _ensure_str_dict(_required_section_var(parsed, "Strings"), "Strings")

    copy_file_sections = _section_names_from_default_install(default_install, "CopyFiles")
    if not copy_file_sections:
        raise ValueError("DefaultInstall 中未找到有效 CopyFiles 节引用, 鼠标指针配置不完整")

    copy_files: dict[str, list[str]] = {}
    for section_name in copy_file_sections:
        if section_name in parsed:
            copy_files[section_name] = _section_constant(parsed, section_name)
    out["CopyFiles"] = copy_files

    for section_name in copy_file_sections:
        cursor_files = copy_files.get(section_name)
        if cursor_files is None:
            continue
        if _looks_like_cursor_file_list(cursor_files):
            out["CursorFiles"] = cursor_files
            out["CursorFilesSection"] = section_name
            break
    else:
        raise ValueError("未找到光标文件复制节, 鼠标指针配置不完整")

    add_reg_sections = _section_names_from_default_install(default_install, "AddReg")
    if not add_reg_sections:
        raise ValueError("DefaultInstall 中未找到有效 AddReg 节引用, 鼠标指针配置不完整")

    add_reg: dict[str, list[str]] = {}
    for section_name in add_reg_sections:
        if section_name in parsed:
            add_reg[section_name] = _section_constant(parsed, section_name)
    out["AddReg"] = add_reg

    for section_name in add_reg_sections:
        scheme_reg = add_reg.get(section_name)
        if scheme_reg:
            out["SchemeReg"] = scheme_reg
            out["SchemeRegSection"] = section_name
            break
    else:
        raise ValueError("未找到方案注册表配置节, 鼠标指针配置不完整")

    return out


def parse_inf_file_content(
    inf_path: Path,
) -> CursorShemeINF:
    """从 INF 文件中获取鼠标指针配置数据

    Args:
        inf_path (Path): 鼠标指针的 INF 配置文件
    Returns:
        CursorShemeINF: 鼠标指针配置数据
    Raises:
        ValueError: 当鼠标指针配置文件不完整时
    """
    inf = parse_inf_file(inf_path)
    return preprocess_inf_to_cursor_scheme(inf)


def dict_to_inf_strings_format(
    data_dict: dict[str, str],
    indent_width: int = 12,
) -> str:
    """将字典转换为 INF 文件 [Strings] 部分的格式

    Args:
        data_dict (dict[str, str]): 包含键值对的字典
        indent_width (int): 缩进宽度, 默认为 12 个空格
    Returns:
        str: 格式化的字符串
    """
    lines = []
    for key, value in data_dict.items():
        # 使用制表符或空格对齐，保持与原格式一致
        separator = "\t\t" if len(key) < indent_width else "\t"
        line = f'{key}{separator}= "{value}"'
        lines.append(line)

    return "\n".join(lines)
