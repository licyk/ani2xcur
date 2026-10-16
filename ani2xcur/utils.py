"""其他工具合集"""

import random
import string
from typing import Any
from pathlib import Path
from urllib.parse import urlparse

from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_COLOR,
    LOGGER_LEVEL,
    LOGGER_NAME,
)


logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def save_convert_to_float(
    value: Any,
) -> float | Any:
    """尝试将值转换为浮点数

    Args:
        value (Any): 用于转换的值
    Returns:
        (float | Any): 转换成功时返回浮点数, 否则返回原始数据
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return value


def safe_convert_to_int(
    value: Any,
) -> int | Any:
    """尝试将值转换为整数

    Args:
        value (Any): 用于转换的值
    Returns:
        (int | Any): 转换成功时返回整数, 否则返回原始数据
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return value


def open_file_as_bytes(
    input_file: Path,
) -> bytes:
    """读取文件并且以二进制模式打开

    Args:
        input_file (Path): 要打开的文件
    Returns:
        bytes: 二进制文件
    Raises:
        FileNotFoundError: 当文件不存在时抛出
        PermissionError: 当权限不足无法读取文件时抛出
        IsADirectoryError: 当路径是目录而不是文件时抛出
        OSError: 当操作系统错误导致无法读取文件时抛出
        Exception: 当发生其他未知错误时抛出
    """
    try:
        with input_file.open("rb") as binary_file:
            return binary_file.read()
    except FileNotFoundError as e:
        logger.error("文件未找到: '%s'", input_file)
        raise e
    except PermissionError as e:
        logger.error("权限不足, 无法读取文件: '%s'", input_file)
        raise e
    except IsADirectoryError as e:
        logger.error("路径是一个目录, 不是文件: '%s'", input_file)
        raise e
    except OSError as e:
        logger.error("操作系统错误, 无法读取文件: '%s', 错误信息: %s", input_file, e)
        raise e
    except Exception as e:
        logger.error("读取文件时发生未知错误: '%s'", input_file)
        raise e


def save_bytes_to_file(
    bytes_file: bytes,
    output_path: Path,
) -> None:
    """将二进制文件保存为文件

    Args:
        bytes_file (bytes): 二进制文件
        output_path (Path): 保存二进制文件的路径
    Raises:
        FileNotFoundError: 当输出目录不存在时抛出
        PermissionError: 当权限不足无法写入文件时抛出
        IsADirectoryError: 当输出路径是目录而不是文件时抛出
        OSError: 当操作系统错误导致无法写入文件时抛出
        Exception: 当发生其他未知错误时抛出
    """
    try:
        with output_path.open("wb") as f:
            f.write(bytes_file)
    except FileNotFoundError as e:
        logger.error("输出目录不存在: '%s'", output_path)
        raise e
    except PermissionError as e:
        logger.error("权限不足, 无法读取文件: '%s'", output_path)
        raise e
    except IsADirectoryError as e:
        logger.error("输出路径是一个目录, 不是文件: '%s'", output_path)
        raise e
    except OSError as e:
        logger.error("操作系统错误, 无法写入文件: '%s', 错误信息: %s", output_path, e)
        raise e
    except Exception as e:
        logger.error("写入输出文件时发生未知错误: '%s'", output_path)
        raise e


def is_utf8_bom_encoding_file(
    file_path: Path,
) -> bool:
    """检测文本文件是否为 UTF8 BOM 编码保存

    Args:
        file_path (Path): 文本文件路径

    Returns:
        bool: 检测结果
    """
    with open(file_path, "rb") as file:
        bom = file.read(3)
        return bom == b"\xef\xbb\xbf"


def detect_encoding(
    file_path: Path,
) -> str:
    """
    检测文件的编码格式

    Args:
        file_path (Path): 文件路径

    Returns:
        str: 检测到的编码格式, 如 'utf-8' 或 'gbk'
    """
    if is_utf8_bom_encoding_file(file_path):
        logger.debug("'%s' 文件编码格式为 UTF8 BOM", file_path)
        return "utf-8-sig"

    with open(file_path, "rb") as f:
        raw_data = f.read()

    try:
        raw_data.decode("utf-8")
        logger.debug("'%s' 文件编码格式为 UTF8", file_path)
        return "utf-8"
    except UnicodeDecodeError:
        logger.debug("'%s' 文件编码格式为 GBK", file_path)
        return "gbk"


def lowercase_dict_keys(
    d: dict[str, Any],
) -> dict[str, Any]:
    """
    递归地将字典中的键转换为小写形式, 但如果转换后会导致键重复, 则保留原键名不变. 同时处理嵌套的字典

    Args:
        d (dict[str, Any]): 输入的字典

    Returns:
        (dict[str, Any]): 处理后的新字典
    """
    if not isinstance(d, dict):
        return d

    # 用于存储转换后的键值对
    new_dict = {}
    # 用于记录准备转换的键，以检查转换后是否会产生冲突
    lower_key_mapping = {}

    # 首先收集所有键及其转换为小写后的形式
    for key, value in d.items():
        lower_key = key.lower() if isinstance(key, str) else key
        if lower_key in lower_key_mapping:
            # 如果小写后的键已经存在, 说明会产生冲突, 将这两个键都保留原样
            lower_key_mapping[lower_key] = None  # 标记为冲突
        else:
            lower_key_mapping[lower_key] = key  # 存储原始键

    # 构建新字典
    for key, value in d.items():
        # 检查这个键的小写形式是否与其他键冲突
        lower_key = key.lower() if isinstance(key, str) else key

        # 如果键是字符串且小写形式映射到多个原始键 (即存在冲突), 则保留原键
        if isinstance(key, str) and lower_key_mapping.get(lower_key) is None:
            final_key = key  # 保留原始键
        # 如果小写键只对应一个原始键, 则使用小写键
        elif isinstance(key, str) and lower_key_mapping.get(lower_key) == key:
            final_key = lower_key
        else:
            final_key = key  # 非字符串键保持不变

        # 递归处理值
        if isinstance(value, dict):
            new_dict[final_key] = lowercase_dict_keys(value)
        elif isinstance(value, list):
            # 如果值是列表, 检查列表中的每个元素是否为字典
            new_dict[final_key] = [lowercase_dict_keys(item) if isinstance(item, dict) else item for item in value]
        else:
            new_dict[final_key] = value

    return new_dict


def extend_list_to_length(
    lst: list[Any],
    target_length: int,
    fill_value: str | None = "",
) -> list[Any]:
    """将列表扩展到指定长度

    Args:
        lst (list[Any]): 原始列表
        target_length (int): 扩充到的指定长度
        fill_value (str | None): 填充的内容
    Returns:
        list[Any]: 扩展长度后的列表
    """
    if len(lst) < target_length:
        lst.extend([fill_value] * (target_length - len(lst)))
    return lst


def generate_random_string(
    length: int = 8,
    chars: str | None = None,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    include_digits: bool = True,
    include_special: bool = False,
) -> str:
    """生成随机字符串

    Args:
        length (int): 字符串长度, 默认为 8
        chars (str | None): 自定义字符集, 如果提供则忽略其他参数
        include_uppercase (bool): 是否包含大写字母
        include_lowercase (bool): 是否包含小写字母
        include_digits (bool): 是否包含数字
        include_special (bool): 是否包含特殊字符
    Returns:
        str: 生成的随机字符串
    Raises:
        ValueError: 字符池为空时
    """
    if chars is not None:
        char_pool = chars
    else:
        char_pool = ""
        if include_uppercase:
            char_pool += string.ascii_uppercase
        if include_lowercase:
            char_pool += string.ascii_lowercase
        if include_digits:
            char_pool += string.digits
        if include_special:
            char_pool += "!@#$%^&*"

    if not char_pool:
        raise ValueError("字符池不能为空")

    return "".join(random.choice(char_pool) for _ in range(length))


def is_http_or_https(url: str) -> bool:
    """检测字符串是否为 HTTP / HTTPS 链接

    Args:
        url (str): 待检测的字符串

    Returns:
        bool: 如果是 HTTPS / HTTP 链接返回 True
    """
    try:
        result = urlparse(url)
        # result.scheme 获取协议部分 (如 http, https)
        # result.netloc 确保有域名部分 (避免 "https://" 这种空链接)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False
