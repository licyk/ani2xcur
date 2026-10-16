"""Windows 桌面环境配置工具"""

import ctypes
import os
import re
from typing import Any

from ani2xcur.manager.regedit import (
    registry_query_value,
    registry_set_value,
    registry_enum_values,
    RegistryAccess,
    RegistryRootKey,
    RegistryValueType,
)
from ani2xcur.utils import (
    extend_list_to_length,
    lowercase_dict_keys,
)
from ani2xcur.manager.base import CURSOR_KEYS
from ani2xcur.manager.desktop_config.base import (
    convert_windows_cursor_base_size_to_size,
    convert_windows_cursor_size_to_base_size,
)

WINDOWS_CURSOR_CURSORS_PATH = r"Control Panel\Cursors"
"""Windows 鼠标指针配置路径"""

WINDOWS_CURSOR_CURSORS_SCHEME_PATH = r"Control Panel\Cursors\Schemes"
"""Windows 鼠标指针方案路径"""

WINDOWS_ACCESSIBILITY_PATH = r"Software\Microsoft\Accessibility"
"""Windows 无障碍配置路径"""

WINDOWS_CURSOR_SIZE_VALUE_NAME = "CursorSize"
"""Windows 无障碍鼠标指针大小值名"""

WINDOWS_CURSOR_BASE_SIZE_VALUE_NAME = "CursorBaseSize"
"""Windows 鼠标指针基础大小值名"""

SPI_SETCURSORS = 0x0057
"""重新加载系统鼠标指针"""

SPI_SETCURSORBASESIZE = 0x2029
"""应用 Windows 鼠标指针基础大小"""

SPIF_UPDATEINIFILE = 0x01
"""将系统参数写入用户配置"""

SPIF_SENDCHANGE = 0x02
"""广播系统参数变更"""

SPIF_APPLY_CHANGE = SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
"""应用并广播系统参数变更"""


def has_var_string(
    text: str,
) -> bool:
    """检测字符串中是否包含 %var% 格式的变量

    Args:
        text (str): 需要检测的字符串
    Returns:
        bool: 如果字符串中存在 %var% 格式的变量则返回 True, 否则返回 False
    """
    pattern = r"%([^%]+)%"
    return bool(re.search(pattern, text))


def expand_var_string(
    text: str,
    vars_dict: dict[str, str] | None = None,
) -> str:
    """将字符串中的 %var% 变量进行替换, 并优先查找变量表中的值

    Args:
        text (str): 需要处理的字符串
        vars_dict (dict[str, str] | None): 变量字典
    Returns:
        str: 处理后的字符串
    """

    effective_vars = lowercase_dict_keys(vars_dict or {})

    def _replace_env_var(
        match: re.Match,
    ) -> str:
        env_var = match.group(1)
        env_var_lower = match.group(1).lower().strip()
        return effective_vars.get(env_var_lower, os.environ.get(env_var, match.group(0)))

    pattern = r"%([^%]+)%"
    text = text.replace(r"%10%", r"%SYSTEMROOT%")
    result = re.sub(pattern, _replace_env_var, text)
    return result


def _ctypes_windll() -> Any:
    windll = getattr(ctypes, "windll", None)
    if windll is None:
        raise NotImplementedError("Windows 系统参数 API 只能在 Windows 系统中使用")
    return windll


def system_parameters_info(
    action: int,
    ui_param: int = 0,
    pv_param: int | None = 0,
    flags: int = 0,
) -> bool:
    """调用 Windows SystemParametersInfoW

    Args:
        action (int): 要执行的系统参数操作
        ui_param (int): 操作需要的整数参数
        pv_param (int | None): 操作需要的值参数
        flags (int): 应用系统参数时使用的标志位

    Returns:
        bool: 调用成功时返回 True, 否则返回 False

    参考资料:
        https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow
    """
    return bool(_ctypes_windll().user32.SystemParametersInfoW(action, ui_param, pv_param, flags))


def refresh_system_params(
    cursor_base_size: int | None = None,
) -> None:
    """通知系统刷新设置以应用更改

    参考资料:
    - SystemParametersInfoW: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow
    - PowerShell 刷新光标大小讨论: https://stackoverflow.com/questions/60104778/change-and-update-the-size-of-the-cursor-in-windows-10-via-powershell
    - Windows 11 光标刷新讨论: https://www.elevenforum.com/t/reloading-mouse-cursors-and-changing-their-size.37551/

    Args:
        cursor_base_size (int | None): Windows 鼠标指针基础大小, 传入时会同步应用当前会话中的指针大小
    """
    if cursor_base_size is not None:
        system_parameters_info(SPI_SETCURSORBASESIZE, 0, cursor_base_size, SPIF_APPLY_CHANGE)

    if not system_parameters_info(SPI_SETCURSORS, 0, 0, SPIF_APPLY_CHANGE):
        if not system_parameters_info(SPI_SETCURSORS, 0, 0, SPIF_SENDCHANGE):
            system_parameters_info(SPI_SETCURSORS, 0, 0, 0)


def get_windows_cursor_theme() -> str | None:
    """获取 Windows 桌面当前使用的鼠标指针配置名称

    Returns:
        (str | None): 当前使用的鼠标指针名称
    """
    cursor_theme = registry_query_value(
        name="",
        sub_key=WINDOWS_CURSOR_CURSORS_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.READ,
    )
    return cursor_theme if isinstance(cursor_theme, str) else None


def get_windows_cursor_size() -> int | None:
    """获取 Windows 桌面当前使用的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    cursor_size = registry_query_value(
        name=WINDOWS_CURSOR_SIZE_VALUE_NAME,
        sub_key=WINDOWS_ACCESSIBILITY_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.READ,
    )
    if isinstance(cursor_size, int):
        return cursor_size

    cursor_base_size = registry_query_value(
        name=WINDOWS_CURSOR_BASE_SIZE_VALUE_NAME,
        sub_key=WINDOWS_CURSOR_CURSORS_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.READ,
    )
    if not isinstance(cursor_base_size, int):
        return None
    return convert_windows_cursor_base_size_to_size(cursor_base_size)


def set_windows_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 Windows 桌面当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    # 获取鼠标指针方案列表
    schemes = registry_enum_values(
        sub_key=WINDOWS_CURSOR_CURSORS_SCHEME_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.READ,
    )
    if cursor_name not in schemes:
        return

    scheme_data = schemes[cursor_name]
    if not isinstance(scheme_data, str):
        return
    cursor_paths = [x for x in extend_list_to_length(scheme_data.split(","), target_length=len(CURSOR_KEYS["win"]))]

    # 设置方案名称
    registry_set_value(
        name="",
        value=cursor_name,
        reg_type=RegistryValueType.SZ,
        sub_key=WINDOWS_CURSOR_CURSORS_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.SET_VALUE,
    )

    # 设置鼠标指针对应的文件路径
    for cursor, path in zip(CURSOR_KEYS["win"], cursor_paths):
        reg_type = RegistryValueType.EXPAND_SZ if has_var_string(path) else RegistryValueType.SZ
        registry_set_value(
            name=cursor,
            value=path,
            reg_type=reg_type,
            sub_key=WINDOWS_CURSOR_CURSORS_PATH,
            key=RegistryRootKey.CURRENT_USER,
            access=RegistryAccess.SET_VALUE,
        )

    refresh_system_params()


def set_windows_cursor_size(
    cursor_size: int,
) -> None:
    """设置 Windows 桌面当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    """
    cursor_base_size = convert_windows_cursor_size_to_base_size(cursor_size)
    registry_set_value(
        name=WINDOWS_CURSOR_SIZE_VALUE_NAME,
        value=cursor_size,
        reg_type=RegistryValueType.DWORD,
        sub_key=WINDOWS_ACCESSIBILITY_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.SET_VALUE,
    )
    registry_set_value(
        name=WINDOWS_CURSOR_BASE_SIZE_VALUE_NAME,
        value=cursor_base_size,
        reg_type=RegistryValueType.DWORD,
        sub_key=WINDOWS_CURSOR_CURSORS_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.SET_VALUE,
    )
    refresh_system_params(cursor_base_size=cursor_base_size)
