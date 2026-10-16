"""GTK xsettings 环境配置工具"""

from pathlib import Path

from ani2xcur.config import LOGGER_COLOR, LOGGER_LEVEL, LOGGER_NAME
from ani2xcur.logger import get_logger
from ani2xcur.utils import safe_convert_to_int

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)

GTK_XSETTINGS_PATH = Path("~/.config/xsettingsd/xsettingsd.conf").expanduser()
"""GTK xsettings 配置文件路径"""


def read_gtk_xsettings_config(
    config_path: Path,
) -> dict[str, str | int]:
    """读取 GTK xsettings 配置文件并返回配置字典

    Args:
        config_path (Path): GTK xsettings 配置文件路径
    Returns:
        (dict[str, str | int]): 配置字典
    """
    config: dict[str, str | int] = {}

    logger.debug("读取 GTK xsettings 配置文件: '%s'", config_path)
    with open(config_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            # 跳过注释行和空行
            if line.startswith("#") or not line:
                continue

            # 分割键和值
            parts = line.split(maxsplit=1)  # 只分割第一个空格
            if len(parts) != 2:
                continue

            key = parts[0].strip()
            value = parts[1].strip()

            # 移除值两端的引号（如果有的话）
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            config[key] = value

    logger.debug("读取 GTK xsettings 配置完成: keys=%s", sorted(config))
    return config


def write_gtk_xsettings_config(
    config_path: Path,
    config: dict[str, str | int],
) -> None:
    """将配置字典写入 GTK xsettings 配置文件

    Args:
        config_path (Path): GTK xsettings 配置文件路径
        config (dict[str, str | int]): 要写入的配置字典
    """
    with open(config_path, "w", encoding="utf-8") as file:
        for key, value in config.items():
            # 根据值类型决定是否加引号（字符串通常需要加引号）
            if isinstance(value, str):
                file.write(f'{key} "{value}"\n')
            else:
                file.write(f"{key} {value}\n")
    logger.debug("写入 GTK xsettings 配置文件: '%s', keys=%s", config_path, sorted(config))


def get_gtk_xsettings_cursor_theme() -> str | None:
    """获取 GTK xsettings 配置文件中的鼠标指针主题

    Returns:
        (str | None): 当前使用的鼠标指针主题名称
    """
    if not GTK_XSETTINGS_PATH.is_file():
        logger.debug("GTK xsettings 配置文件不存在, 无法读取光标主题: '%s'", GTK_XSETTINGS_PATH)
        return None

    config = read_gtk_xsettings_config(GTK_XSETTINGS_PATH)
    theme = config.get("Gtk/CursorThemeName")
    logger.debug("GTK xsettings 当前光标主题读取结果: %r", theme)
    return theme if isinstance(theme, str) else None


def get_gtk_xsettings_cursor_size() -> int | None:
    """获取 GTK xsettings 配置文件中的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    if not GTK_XSETTINGS_PATH.is_file():
        logger.debug("GTK xsettings 配置文件不存在, 无法读取光标大小: '%s'", GTK_XSETTINGS_PATH)
        return None

    config = read_gtk_xsettings_config(GTK_XSETTINGS_PATH)
    size = safe_convert_to_int(config.get("Gtk/CursorThemeSize"))
    logger.debug("GTK xsettings 当前光标大小读取结果: %r", size)
    return size if isinstance(size, int) else None


def set_gtk_xsettings_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 GTK xsettings 配置文件中的鼠标指针主题

    Args:
        cursor_name (str): 鼠标指针主题名称
    """
    GTK_XSETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if GTK_XSETTINGS_PATH.is_file():
        config = read_gtk_xsettings_config(GTK_XSETTINGS_PATH)
    else:
        config = {}

    config["Gtk/CursorThemeName"] = cursor_name
    logger.debug("写入 GTK xsettings 光标主题: %s", cursor_name)
    write_gtk_xsettings_config(GTK_XSETTINGS_PATH, config)


def set_gtk_xsettings_cursor_size(
    cursor_size: int,
) -> None:
    """设置 GTK xsettings 配置文件中的鼠标指针大小

    Args:
        cursor_size (int): 鼠标指针大小
    """
    GTK_XSETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if GTK_XSETTINGS_PATH.is_file():
        config = read_gtk_xsettings_config(GTK_XSETTINGS_PATH)
    else:
        config = {}

    config["Gtk/CursorThemeSize"] = str(cursor_size)
    logger.debug("写入 GTK xsettings 光标大小: %s", cursor_size)
    write_gtk_xsettings_config(GTK_XSETTINGS_PATH, config)
