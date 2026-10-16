"""Linux 鼠标指针配置文件解析"""

from pathlib import Path
from typing import (
    Any,
    Literal,
    Protocol,
    TypedDict,
)

from ani2xcur.config_parse.parse import (
    ParsedINF,
    parse_inf_file,
)


CursorShemeDesktopEntry = TypedDict(
    "CursorShemeDesktopEntry",
    {
        "Icon Theme": dict[str, str | list[str]],  # 鼠标指针信息
    },
    total=False,
)
"""预处理后的鼠标指针配置 DesktopEntry 结构"""
DesktopEntrySectionName = Literal[
    "Icon Theme",  # 鼠标指针信息
]
"""DesktopEntry 文件已知键名"""


class DesktopEntrySectionDict(Protocol):
    """DesktopEntry 选项结构字典"""

    def get(  # pylint: disable=missing-function-docstring
        self,
        key: Literal["var", "constant"],
        default: Any = ...,
    ) -> str | dict[str, str | list[str]] | Any:
        """获取 DesktopEntry 节中的指定字段。

        Args:
            key: 要获取的字段名
            default: 字段不存在时返回的默认值
        Returns:
            str | dict[str, str | list[str]] | Any: 字段值或默认值
        """
        ...


class KnownDesktopEntrySections(Protocol):
    """已知的 DesktopEntry 结构"""

    def __getitem__(
        self,
        key: DesktopEntrySectionName,
    ) -> DesktopEntrySectionDict: ...
    def __contains__(
        self,
        key: object,
    ) -> bool: ...


def _section_var(
    parsed: ParsedINF,
    section_name: str,
) -> dict[str, str | list[str]]:
    """获取指定节中的变量映射，并保留解析器返回的具体类型。"""
    return parsed[section_name].get("var", {})


def preprocess_desktop_entry_to_cursor_scheme(
    parsed: ParsedINF,
) -> CursorShemeDesktopEntry:
    """将 ParsedDesktopEntry 处理为鼠标指针已知键的扁平结构

    返回包含常见节的字典:
    - Icon Theme: 该节的 var & constant 鼠标指针信息 (若存在)

    Args:
        parsed (ParsedINF): DesktopEntry 类型字典
    Returns:
        CursorShemeDesktopEntry: 预处理后的鼠标指针 DesktopEntry 信息字典
    Raises:
        ValueError: 当鼠标指针配置文件不完整时
    """

    if "Icon Theme" not in parsed:
        raise ValueError("未找到 Icon Theme 键, 鼠标指针配置不完整")

    return {"Icon Theme": _section_var(parsed, "Icon Theme")}


def parse_desktop_entry_content(
    desktop_entry_path: Path,
) -> CursorShemeDesktopEntry:
    """从 DesktopEntry 文件中获取鼠标指针配置数据

    Args:
        desktop_entry_path (Path): 鼠标指针的 DesktopEntry 配置文件
    Returns:
        CursorShemeDesktopEntry: 鼠标指针配置数据
    Raises:
        ValueError: 当鼠标指针配置文件不完整时
    """
    desktop_entry = parse_inf_file(desktop_entry_path)
    return preprocess_desktop_entry_to_cursor_scheme(desktop_entry)


def dict_to_desktop_entry_strings_format(
    data_dict: dict[str, str],
) -> str:
    """
    将字典转换为 Desktop Entry 文件 [<Var>] 部分的格式

    Args:
        data_dict (dict[str, str]): 包含键值对的字典

    Returns:
        str: 格式化的字符串
    """
    lines = []
    for key, value in data_dict.items():
        # 使用制表符或空格对齐，保持与原格式一致
        line = f"{key}={value}"
        lines.append(line)

    return "\n".join(lines)
