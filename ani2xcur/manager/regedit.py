"""Windows 注册表操作工具"""

import sys
from enum import (
    IntFlag,
    auto,
    Enum,
)
from typing import Any


if sys.platform == "win32":
    import winreg as winreg

    class RegistryRootKey(IntFlag):
        """注册表根路径"""

        CLASSES_ROOT = winreg.HKEY_CLASSES_ROOT
        """HKEY_CLASSES_ROOT: 包含所有已注册的文件类型、扩展名与 COM 类信息"""

        CURRENT_USER = winreg.HKEY_CURRENT_USER
        """HKEY_CURRENT_USER: 当前登录用户的配置分支"""

        LOCAL_MACHINE = winreg.HKEY_LOCAL_MACHINE
        """HKEY_LOCAL_MACHINE: 计算机级别的全局配置"""

        USERS = winreg.HKEY_USERS
        """HKEY_USERS: 所有用户配置的根节点"""

        CURRENT_CONFIG = winreg.HKEY_CURRENT_CONFIG
        """HKEY_CURRENT_CONFIG: 当前硬件配置视图"""

        def __int__(
            self,
        ) -> int:
            return self.value

    class RegistryAccess(IntFlag):
        """注册表访问权限"""

        READ = winreg.KEY_READ
        """读取键值"""

        WRITE = winreg.KEY_WRITE
        """写入 / 修改键值"""

        SET_VALUE = winreg.KEY_SET_VALUE
        """只允许写键值"""

        QUERY_VALUE = winreg.KEY_QUERY_VALUE
        """只允许读键值"""

        CREATE_SUB_KEY = winreg.KEY_CREATE_SUB_KEY
        """允许创建子键"""

        ENUMERATE_SUB_KEYS = winreg.KEY_ENUMERATE_SUB_KEYS
        """允许枚举子键"""

        NOTIFY = winreg.KEY_NOTIFY
        """注册表变更通知"""

        ALL_ACCESS = winreg.KEY_ALL_ACCESS
        """完全控制"""

        WOW64_64KEY = winreg.KEY_WOW64_64KEY
        """强制访问 64 位注册表视图"""

        WOW64_32KEY = winreg.KEY_WOW64_32KEY
        """强制访问 32 位注册表视图"""

        def __int__(
            self,
        ) -> int:
            return self.value

    class RegistryValueType(IntFlag):
        """注册表值类型"""

        SZ = winreg.REG_SZ
        """普通字符串 -> `str`"""

        EXPAND_SZ = winreg.REG_EXPAND_SZ
        """可展开字符串 (含 %PATH% 等变量) -> `str`"""

        DWORD = winreg.REG_DWORD
        """32 位整数 -> `int`"""

        QWORD = winreg.REG_QWORD
        """64 位整数 -> `int`"""

        BINARY = winreg.REG_BINARY
        """二进制数据 -> `bytes`"""

        MULTI_SZ = winreg.REG_MULTI_SZ
        """多字符串数组 -> `list[str]`"""

        NONE = winreg.REG_NONE
        """无类型数据 -> `bytes` | `None`"""

        def __int__(
            self,
        ) -> int:
            return int(self.value)
else:

    class RegistryRootKey(Enum):  # pylint: disable=missing-class-docstring
        CLASSES_ROOT = auto()
        CURRENT_USER = auto()
        LOCAL_MACHINE = auto()
        USERS = auto()
        CURRENT_CONFIG = auto()

    class RegistryAccess(Enum):  # pylint: disable=missing-class-docstring
        READ = auto()
        WRITE = auto()
        SET_VALUE = auto()
        QUERY_VALUE = auto()
        CREATE_SUB_KEY = auto()
        ENUMERATE_SUB_KEYS = auto()
        NOTIFY = auto()
        ALL_ACCESS = auto()
        WOW64_64KEY = auto()
        WOW64_32KEY = auto()

    class RegistryValueType(Enum):  # pylint: disable=missing-class-docstring
        SZ = auto()
        EXPAND_SZ = auto()
        DWORD = auto()
        QWORD = auto()
        BINARY = auto()
        MULTI_SZ = auto()
        NONE = auto()

    winreg: Any = NotImplemented  # pylint: disable=invalid-name


def _require_windows_registry() -> None:
    if sys.platform != "win32":
        raise NotImplementedError("Windows 注册表 API 只能在 Windows 系统中使用")


def _root_key(key: RegistryRootKey | None) -> int:
    _require_windows_registry()
    root_key = RegistryRootKey.CURRENT_USER if key is None else key
    value: Any = root_key.value
    return int(value)


def _access(access: RegistryAccess | None) -> int:
    _require_windows_registry()
    registry_access = RegistryAccess.READ if access is None else access
    value: Any = registry_access.value
    return int(value)


def _value_type(reg_type: RegistryValueType) -> int:
    _require_windows_registry()
    value: Any = reg_type.value
    return int(value)


def registry_query_value(
    name: str,
    sub_key: str,
    key: RegistryRootKey | None = RegistryRootKey.CURRENT_USER,
    access: RegistryAccess | None = RegistryAccess.READ,
) -> str | int | bytes | list[str] | None:
    """查询注册表中的键

    Args:
        name (str): 要查询的注册表的值名称
        sub_key (str): 目标注册表子键路径 (不包含根键部分)
        key (RegistryRootKey | None): 注册表根键枚举
        access (RegistryAccess | None): 打开注册表键时使用的访问权限标志
    Returns:
        (str | int | bytes | list[str] | None):
            查询到的注册表值数据，根据注册表类型返回不同 Python 类型：

            - `REG_SZ` / `REG_EXPAND_SZ` -> `str`
            - `REG_DWORD` / `REG_QWORD` -> `int`
            - `REG_BINARY` -> `bytes`
            - `REG_MULTI_SZ` -> `list[str]`
            - 当值不存在时返回 `None`
    """
    with winreg.OpenKey(_root_key(key), sub_key, 0, _access(access)) as reg:
        try:
            return winreg.QueryValueEx(reg, name)[0]
        except FileNotFoundError:
            return None


def registry_delete_value(
    name: str,
    sub_key: str,
    key: RegistryRootKey | None = RegistryRootKey.CURRENT_USER,
    access: RegistryAccess | None = RegistryAccess.SET_VALUE,
) -> bool:
    """删除指定注册表键中的值

    Args:
        name (str):
            要删除的注册表值名称

        sub_key (str):
            目标注册表子键路径（不包含根键部分）

        key (RegistryRootKey | None):
            注册表根键枚举

        access (RegistryAccess | None):
            打开注册表键的访问权限

    Returns:
        bool:
            - `True`: 删除成功
            - `False`: 目标值不存在
    """
    with winreg.OpenKey(_root_key(key), sub_key, 0, _access(access)) as reg:
        try:
            winreg.DeleteValue(reg, name)
            return True
        except FileNotFoundError:
            return False


def registry_enum_values(
    sub_key: str,
    key: RegistryRootKey | None = RegistryRootKey.CURRENT_USER,
    access: RegistryAccess | None = RegistryAccess.READ,
) -> dict[str, str | int | bytes | list[str] | None]:
    """枚举指定注册表键下的所有值

    Args:
        sub_key (str):
            目标注册表子键路径

        key (RegistryRootKey | None):
            注册表根键枚举

        access (RegistryAccess | None):
            打开注册表键的访问权限

    Returns:
        (dict[str, str | int | bytes | list[str] | None]):
            键为注册表值名称,
            值为对应的数据内容, 已转换为 Python 原生类型
    """
    values: dict[str, str | int | bytes | list[str] | None] = {}

    with winreg.OpenKey(_root_key(key), sub_key, 0, _access(access)) as reg:
        index = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(reg, index)
                values[name] = value
                index += 1
            except OSError:
                break

    return values


def registry_set_value(
    name: str,
    value: str | int | bytes | list[str],
    reg_type: RegistryValueType,
    sub_key: str,
    key: RegistryRootKey | None = RegistryRootKey.CURRENT_USER,
    access: RegistryAccess | None = RegistryAccess.SET_VALUE,
) -> None:
    """设置或创建注册表值

    Args:
        name (str):
            注册表值名称

        value (str | int | bytes | list[str]):
            要写入的数据内容

        reg_type (RegistryValueType):
            注册表值类型

        sub_key (str):
            目标注册表子键路径

        key (RegistryRootKey | None):
            注册表根键枚举

        access (RegistryAccess | None):
            打开注册表键的访问权限
    """
    with winreg.OpenKey(_root_key(key), sub_key, 0, _access(access)) as reg:
        winreg.SetValueEx(reg, name, 0, _value_type(reg_type), value)


def registry_path_exists(
    sub_key: str,
    key: RegistryRootKey | None = RegistryRootKey.CURRENT_USER,
    access: RegistryAccess | None = RegistryAccess.READ,
) -> bool:
    """检查指定注册表子键路径是否存在

    Args:
        sub_key (str):
            要检查的注册表子键路径 (不包含根键)

        key (RegistryRootKey | None):
            注册表根键

        access (RegistryAccess | None):
            打开注册表时使用的访问权限

    Returns:
        bool:
            - `True`:路径存在
            - `False`: 路径不存在
    """
    try:
        with winreg.OpenKey(_root_key(key), sub_key, 0, _access(access)) as _:
            return True
    except FileNotFoundError:
        return False


def registry_create_path(
    sub_key: str,
    key: RegistryRootKey | None = RegistryRootKey.CURRENT_USER,
    access: RegistryAccess | None = RegistryAccess.WRITE,
) -> None:
    """创建指定注册表子键路径 (若已存在则忽略)

    Args:
        sub_key (str):
            要创建的注册表子键路径 (不包含根键)

        key (RegistryRootKey | None):
            注册表根键

        access (RegistryAccess | None):
            打开/创建子键时的访问权限
    """
    winreg.CreateKeyEx(_root_key(key), sub_key, 0, _access(access))


def registry_delete_path(
    sub_key: str,
    key: RegistryRootKey | None = RegistryRootKey.CURRENT_USER,
) -> bool:
    """删除指定注册表子键路径（必须为空键）

    Args:
        sub_key (str):
            要删除的注册表子键路径（不包含根键）。

        key (RegistryRootKey | None):
            注册表根键，默认为 ``HKEY_CURRENT_USER``。

    Returns:
        bool:
            - `True`: 删除成功
            - `False`: 路径不存在

    Raises:
        RuntimeError: 所选的注册表路径不为空或者不能被删除
    """
    try:
        winreg.DeleteKey(_root_key(key), sub_key)
        return True
    except FileNotFoundError:
        return False
    except OSError as e:
        raise RuntimeError(f"所选的注册表路径不为空或者不能被删除: {sub_key}") from e


def registry_delete_tree(
    sub_key: str,
    key: RegistryRootKey | None = RegistryRootKey.CURRENT_USER,
) -> bool:
    """递归删除注册表子键树

    Args:
        sub_key (str):
            要删除的注册表子键路径 (不包含根键)

        key (RegistryRootKey | None):
            注册表根键

    Returns:
        bool:
            - `True`: 删除成功
            - `False`: 路径不存在
    """
    try:
        with winreg.OpenKey(
            key=_root_key(key),
            sub_key=sub_key,
            reserved=0,
            access=_access(RegistryAccess.READ) | _access(RegistryAccess.WRITE),
        ) as reg:
            while True:
                try:
                    child = winreg.EnumKey(reg, 0)
                    registry_delete_tree(f"{sub_key}\\{child}", key)
                except OSError:
                    break
        winreg.DeleteKey(_root_key(key), sub_key)
        return True
    except FileNotFoundError:
        return False
