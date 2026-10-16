"""GTK 环境配置工具"""

import re
import configparser
from pathlib import Path

from ani2xcur.config import LOGGER_COLOR, LOGGER_LEVEL, LOGGER_NAME
from ani2xcur.logger import get_logger
from ani2xcur.utils import safe_convert_to_int

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)

GTK4_CONFIG_PATH = Path("~/.config/gtk-4.0/settings.ini").expanduser()
"""GTK 4.0 配置文件路径"""

GTK3_CONFIG_PATH = Path("~/.config/gtk-3.0/settings.ini").expanduser()
"""GTK 3.0 配置文件路径"""

GTK2_CONFIG_PATH = Path("~/.gtkrc-2.0").expanduser()
"""GTK 2.0 配置文件路径"""


def read_gtk2_config(
    config_path: Path,
) -> dict[str, str]:
    """读取 GTK 2.0 配置文件并返回配置字典

    Args:
        config_path (Path): GTK 2.0 配置文件路径
    Returns:
        (dict[str, str]): GTK 2.0 配置字典
    """
    config: dict[str, str] = {}

    logger.debug("读取 GTK 2.0 配置文件: '%s'", config_path)
    with open(config_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            # 跳过注释行和空行
            if line.startswith("#") or not line:
                continue

            # 匹配配置项格式: key=value
            match = re.match(r"^(\w+(?:-\w+)*)=(.*)$", line)
            if match:
                key, value = match.groups()
                # 移除值两端的引号 (如果有的话)
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                config[key] = value

    logger.debug("读取 GTK 2.0 配置完成: keys=%s", sorted(config))
    return config


def write_gtk2_config(
    config_path: Path,
    updates: dict[str, str],
) -> None:
    """修改 GTK 2.0 配置文件

    Args:
        config_path (Path): 配置文件路径
        updates (dict[str, str]): 要更新的内容字典
    """
    lines = []
    found_keys = set()

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        stripped = line.strip()
        # 匹配当前的 key
        match = re.match(r"^([\w-]+)=", stripped)
        if match:
            key = match.group(1)
            if key in updates:
                # 针对字符串值，通常 GTK2 推荐使用双引号
                val = updates[key]
                # 如果是数字 (如 size), 直接写; 如果是字符串 (如 theme), 加引号
                # 这里简单处理: 如果输入是纯数字且 key 包含 size, 则不加引号
                if "size" in key or val.isdigit():
                    new_lines.append(f"{key}={val}\n")
                else:
                    new_lines.append(f'{key}="{val}"\n')
                found_keys.add(key)
                continue
        new_lines.append(line)

    # 追加文件中不存在的新配置项
    for key, val in updates.items():
        if key not in found_keys:
            if "size" in key or str(val).isdigit():
                new_lines.append(f"{key}={val}\n")
            else:
                new_lines.append(f'{key}="{val}"\n')

    with open(config_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    logger.debug("写入 GTK 2.0 配置文件: '%s', updates=%s", config_path, updates)


def get_gtk4_cursor_theme() -> str | None:
    """获取 GTK4 标准方案的当前使用的鼠标指针配置名称

    Returns:
        (str | None): 当前使用的鼠标指针名称
    """
    config = configparser.ConfigParser()
    config.read(GTK4_CONFIG_PATH, encoding="utf-8")
    if "Settings" in config and "gtk-cursor-theme-name" in config["Settings"]:
        result = config.get("Settings", "gtk-cursor-theme-name")
        logger.debug("GTK4 当前光标主题读取结果: %r", result)
        return result
    logger.debug("GTK4 配置未提供光标主题: '%s'", GTK4_CONFIG_PATH)
    return None


def get_gtk3_cursor_theme() -> str | None:
    """获取 GTK3 标准方案的当前使用的鼠标指针配置名称

    Returns:
        (str | None): 当前使用的鼠标指针名称
    """
    config = configparser.ConfigParser()
    config.read(GTK3_CONFIG_PATH, encoding="utf-8")
    if "Settings" in config and "gtk-cursor-theme-name" in config["Settings"]:
        result = config.get("Settings", "gtk-cursor-theme-name")
        logger.debug("GTK3 当前光标主题读取结果: %r", result)
        return result
    logger.debug("GTK3 配置未提供光标主题: '%s'", GTK3_CONFIG_PATH)
    return None


def get_gtk2_cursor_theme() -> str | None:
    """获取 GTK2 标准方案的当前使用的鼠标指针配置名称

    Returns:
        (str | None): 当前使用的鼠标指针名称
    """
    if not GTK2_CONFIG_PATH.is_file():
        logger.debug("GTK2 配置文件不存在, 无法读取光标主题: '%s'", GTK2_CONFIG_PATH)
        return None

    config = read_gtk2_config(GTK2_CONFIG_PATH)
    result = config.get("gtk-cursor-theme-name")
    logger.debug("GTK2 当前光标主题读取结果: %r", result)
    return result


def get_gtk4_cursor_size() -> int | None:
    """获取 GTK4 标准方案的当前使用的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    config = configparser.ConfigParser()
    config.read(GTK4_CONFIG_PATH, encoding="utf-8")
    if "Settings" in config and "gtk-cursor-theme-size" in config["Settings"]:
        result = safe_convert_to_int(config.get("Settings", "gtk-cursor-theme-size"))
        logger.debug("GTK4 当前光标大小读取结果: %r", result)
        return result
    logger.debug("GTK4 配置未提供光标大小: '%s'", GTK4_CONFIG_PATH)
    return None


def get_gtk3_cursor_size() -> int | None:
    """获取 GTK3 标准方案的当前使用的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    config = configparser.ConfigParser()
    config.read(GTK3_CONFIG_PATH, encoding="utf-8")
    if "Settings" in config and "gtk-cursor-theme-size" in config["Settings"]:
        result = safe_convert_to_int(config.get("Settings", "gtk-cursor-theme-size"))
        logger.debug("GTK3 当前光标大小读取结果: %r", result)
        return result
    logger.debug("GTK3 配置未提供光标大小: '%s'", GTK3_CONFIG_PATH)
    return None


def get_gtk2_cursor_size() -> int | None:
    """获取 GTK2 标准方案的当前使用的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    if not GTK2_CONFIG_PATH.is_file():
        logger.debug("GTK2 配置文件不存在, 无法读取光标大小: '%s'", GTK2_CONFIG_PATH)
        return None

    config = read_gtk2_config(GTK2_CONFIG_PATH)
    result = safe_convert_to_int(config.get("gtk-cursor-theme-size"))
    logger.debug("GTK2 当前光标大小读取结果: %r", result)
    return result


def set_gtk4_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 GTK4 标准方案的当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    GTK4_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config.read(GTK4_CONFIG_PATH, encoding="utf-8")
    if "Settings" not in config:
        config["Settings"] = {}

    config["Settings"]["gtk-cursor-theme-name"] = cursor_name
    logger.debug("写入 GTK4 光标主题: %s -> '%s'", cursor_name, GTK4_CONFIG_PATH)
    with open(GTK4_CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f, space_around_delimiters=False)


def set_gtk3_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 GTK3 标准方案的当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    GTK3_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config.read(GTK3_CONFIG_PATH, encoding="utf-8")
    if "Settings" not in config:
        config["Settings"] = {}

    config["Settings"]["gtk-cursor-theme-name"] = cursor_name
    logger.debug("写入 GTK3 光标主题: %s -> '%s'", cursor_name, GTK3_CONFIG_PATH)
    with open(GTK3_CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f, space_around_delimiters=False)


def set_gtk2_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 GTK2 标准方案的当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    GTK2_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("写入 GTK2 光标主题: %s -> '%s'", cursor_name, GTK2_CONFIG_PATH)
    write_gtk2_config(config_path=GTK2_CONFIG_PATH, updates={"gtk-cursor-theme-name": cursor_name})


def set_gtk4_cursor_size(
    cursor_size: int,
) -> None:
    """设置 GTK4 标准方案的当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    """
    GTK4_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config.read(GTK4_CONFIG_PATH, encoding="utf-8")
    if "Settings" not in config:
        config["Settings"] = {}

    config["Settings"]["gtk-cursor-theme-size"] = str(cursor_size)
    logger.debug("写入 GTK4 光标大小: %s -> '%s'", cursor_size, GTK4_CONFIG_PATH)
    with open(GTK4_CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f, space_around_delimiters=False)


def set_gtk3_cursor_size(
    cursor_size: int,
) -> None:
    """设置 GTK3 标准方案的当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    """
    GTK3_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config.read(GTK3_CONFIG_PATH, encoding="utf-8")
    if "Settings" not in config:
        config["Settings"] = {}

    config["Settings"]["gtk-cursor-theme-size"] = str(cursor_size)
    logger.debug("写入 GTK3 光标大小: %s -> '%s'", cursor_size, GTK3_CONFIG_PATH)
    with open(GTK3_CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f, space_around_delimiters=False)


def set_gtk2_cursor_size(
    cursor_size: int,
) -> None:
    """设置 GTK2 标准方案的当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    """
    GTK2_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("写入 GTK2 光标大小: %s -> '%s'", cursor_size, GTK2_CONFIG_PATH)
    write_gtk2_config(config_path=GTK2_CONFIG_PATH, updates={"gtk-cursor-theme-size": str(cursor_size)})
