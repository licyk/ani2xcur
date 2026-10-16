"""桌面环境配置"""

import os
from typing import NamedTuple

from ani2xcur.config import LOGGER_COLOR, LOGGER_LEVEL, LOGGER_NAME
from ani2xcur.logger import get_logger

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


class IntRange(NamedTuple):
    """整数范围"""

    min: int
    """最小值"""

    max: int
    """最大值"""


WINDOWS_CURSOR_SIZE_RANGE = IntRange(1, 15)
"""Windows 鼠标指针大小有效值范围, 对应 Windows 11 设置中的滑块档位"""

WINDOWS_CURSOR_BASE_SIZE_RANGE = IntRange(32, 256)
"""Windows CursorBaseSize 有效值范围"""

WINDOWS_CURSOR_BASE_SIZE_STEP = 16
"""Windows CursorBaseSize 每个滑块档位增加的大小"""

LINUX_CURSOR_SIZE_RANGE = IntRange(16, 96)
"""Linux 鼠标指针大小有效值范围"""


def get_linux_session_type() -> str | None:
    """获取当前 Linux 图形会话类型。

    Returns:
        str | None: 当前图形会话类型, 无法获取时返回 None。
    """
    session_type = os.environ.get("XDG_SESSION_TYPE", "").strip().casefold()
    logger.debug("当前 XDG_SESSION_TYPE=%r", session_type or None)
    return session_type or None


def is_wayland_session() -> bool:
    """检测当前会话是否为 Wayland 或 Wayland + XWayland 环境。

    Returns:
        bool: 当前会话是 Wayland 或 Wayland + XWayland 环境时返回 True。
    """
    session_type = get_linux_session_type()
    if session_type == "wayland":
        logger.debug("检测到明确的 Wayland 会话")
        return True
    if session_type == "x11":
        logger.debug("检测到明确的 X11 会话")
        return False

    result = bool(os.environ.get("WAYLAND_DISPLAY")) and bool(os.environ.get("DISPLAY"))
    logger.debug(
        "会话类型未知, 根据 DISPLAY=%r 和 WAYLAND_DISPLAY=%r 判断 Wayland/XWayland=%s",
        os.environ.get("DISPLAY"),
        os.environ.get("WAYLAND_DISPLAY"),
        result,
    )
    return result


def check_windows_cursor_size_value(
    value: int,
) -> int:
    """检查设置的 Windows 鼠标指针大小是否符合范围

    Args:
        value (int): 鼠标指针大小
    Returns:
        int: 校验通过后的鼠标指针大小
    Raises:
        TypeError: 鼠标指针大小不是 int 时
        ValueError: 鼠标指针大小超过有效范围时
    """
    rng = WINDOWS_CURSOR_SIZE_RANGE
    if not isinstance(value, int):
        raise TypeError(f"Windows 鼠标指针大小值应为 int 类型, 但得到 {type(value).__name__} 类型")
    if rng.min <= value <= rng.max:
        return value
    raise ValueError(f"Windows 鼠标指针大小的值 {value} 超过有效范围 [{rng.min}, {rng.max}]")


def convert_windows_cursor_size_to_base_size(
    value: int,
) -> int:
    """将 Windows 设置页中的鼠标指针大小档位转换为 CursorBaseSize 值

    Args:
        value (int): Windows 设置页中的鼠标指针大小档位
    Returns:
        int: CursorBaseSize 注册表值
    """
    check_windows_cursor_size_value(value)
    return WINDOWS_CURSOR_BASE_SIZE_RANGE.min + (value - WINDOWS_CURSOR_SIZE_RANGE.min) * WINDOWS_CURSOR_BASE_SIZE_STEP


def convert_windows_cursor_base_size_to_size(
    value: int,
) -> int | None:
    """将 CursorBaseSize 值转换为 Windows 设置页中的鼠标指针大小档位

    Args:
        value (int): CursorBaseSize 注册表值
    Returns:
        int | None: 对应的鼠标指针大小档位, 无法匹配时返回 None
    Raises:
        TypeError: CursorBaseSize 值不是 int 时
    """
    rng = WINDOWS_CURSOR_BASE_SIZE_RANGE
    if not isinstance(value, int):
        raise TypeError(f"Windows CursorBaseSize 值应为 int 类型, 但得到 {type(value).__name__} 类型")
    if not rng.min <= value <= rng.max:
        return None

    offset = value - rng.min
    if offset % WINDOWS_CURSOR_BASE_SIZE_STEP != 0:
        return None
    return WINDOWS_CURSOR_SIZE_RANGE.min + offset // WINDOWS_CURSOR_BASE_SIZE_STEP


def check_linux_cursor_size_value(
    value: int,
) -> int:
    """检查设置的 Linux 鼠标指针大小是否符合范围

    Args:
        value (int): 鼠标指针大小
    Returns:
        int: 校验通过后的鼠标指针大小
    Raises:
        TypeError: 鼠标指针大小不是 int 时
        ValueError: 鼠标指针大小超过有效范围时
    """
    rng = LINUX_CURSOR_SIZE_RANGE
    if not isinstance(value, int):
        raise TypeError(f"Linux 鼠标指针大小值应为 int 类型, 但得到 {type(value).__name__} 类型")
    if rng.min <= value <= rng.max:
        return value
    raise ValueError(f"Linux 鼠标指针大小的值 {value} 超过有效范围 [{rng.min}, {rng.max}]")
