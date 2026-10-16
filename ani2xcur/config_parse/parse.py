"""配置文件解析"""

import re
from pathlib import Path
from typing import (
    TypedDict,
    TypeAlias,
)


from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_LEVEL,
    LOGGER_COLOR,
    LOGGER_NAME,
)
from ani2xcur.utils import detect_encoding

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


class INFSection(TypedDict, total=False):
    """INF 文件内容结构"""

    var: dict[str, str | list[str]]
    constant: list[str]


ParsedINF: TypeAlias = dict[str, INFSection]  # pylint: disable=invalid-name
"""已解析 INF 的类型"""


def parse_inf_text(
    text: str,
) -> ParsedINF:
    """解析 INF 文本
    Args:
        text (str): INF 文本字符串
    Returns:
        ParsedINF: INF 文件结构字典
    """
    result: ParsedINF = {}
    current: str | None = None

    # 按行处理, 去除注释行（以 ; 或 // 开头 或 全为 / 的分隔行）
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(";") or line.startswith("//") or set(line) <= {"/"}:
            continue

        m = re.match(r"^\[(.+?)\]$", line)
        if m:
            current = m.group(1)
            result[current] = {"var": {}, "constant": []}
            continue

        if current is None:
            continue

        if "=" in line:
            # 变量 = 值 (值可能包含逗号和引号)
            key, rhs = line.split("=", 1)
            key = key.strip()
            rhs_raw = rhs.strip()

            # 如果整段值被一对外层引号包裹 -> 去掉外层引号, 作为单一字符串
            if rhs_raw.startswith('"') and rhs_raw.endswith('"'):
                val = rhs_raw[1:-1]
            else:
                # 按逗号分割, 但避免拆分引号内的逗号 (使用正则)
                parts = [p.strip() for p in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', rhs_raw)]
                # 如果只有一项则返回字符串, 否则返回列表
                # 注意: 不去掉内部项的引号 (除非整体被引号包裹)
                val = parts[0] if len(parts) == 1 else parts

            result[current]["var"][key] = val
        else:
            # 常量行: 单独一项，若被外层引号包裹则去除外层引号
            const = line
            if const.startswith('"') and const.endswith('"'):
                const = const[1:-1]
            result[current]["constant"].append(const)

    return result


def parse_inf_file(
    path: Path,
) -> ParsedINF:
    """解析 INF 文件

    Args:
        path (Path): INF 文件路径
    Returns:
        ParsedINF: INF 文件结构字典
    """
    with open(path, "r", encoding=detect_encoding(path), errors="ignore") as f:
        return parse_inf_text(f.read())
