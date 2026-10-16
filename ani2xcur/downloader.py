"""下载工具"""

import hashlib
from pathlib import Path
from urllib.parse import urlparse

from tqdm import tqdm

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


def download_file_from_url(
    url: str,
    save_path: Path | None = None,
    file_name: str | None = None,
    progress: bool | None = True,
    hash_prefix: str | None = None,
    re_download: bool | None = False,
) -> Path:
    """使用 requests 库下载文件

    Args:
        url (str): 下载链接
        save_path (Path | None): 下载路径
        file_name (str | None): 保存的文件名, 如果为 None 则从 url 中提取
        progress (bool | None): 是否启用下载进度条
        hash_prefix (str | None): sha256 十六进制前缀, 提供时会校验下载文件
        re_download (bool | None): 是否强制重新下载文件
    Returns:
        Path: 下载后的文件路径
    Raises:
        ValueError: 文件哈希值与预期前缀不匹配时
    """
    import requests

    if save_path is None:
        save_path = Path.cwd()

    if not file_name:
        parts = urlparse(url)
        file_name = Path(parts.path).name

    cached_file = save_path.resolve() / file_name

    if re_download or not cached_file.exists():
        save_path.mkdir(parents=True, exist_ok=True)
        temp_file = save_path / f"{file_name}.tmp"
        logger.info("下载 '%s' 到 '%s' 中", file_name, cached_file)
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=file_name,
            disable=not progress,
        ) as progress_bar:
            with open(temp_file, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))

        if hash_prefix and not compare_sha256(temp_file, hash_prefix):
            logger.error("'%s' 的哈希值不匹配, 正在删除临时文件", temp_file)
            temp_file.unlink()
            raise ValueError(f"文件哈希值与预期的哈希前缀不匹配: {hash_prefix}")

        temp_file.rename(cached_file)
        logger.info("'%s' 下载完成", file_name)
    else:
        logger.info("'%s' 已存在于 '%s' 中", file_name, cached_file)
    return cached_file


def compare_sha256(
    file_path: str | Path,
    hash_prefix: str,
) -> bool:
    """检查文件的 sha256 哈希值是否与给定的前缀匹配

    Args:
        file_path (str | Path): 文件路径
        hash_prefix (str): 哈希前缀
    Returns:
        bool: 匹配结果
    """
    hash_sha256 = hashlib.sha256()
    blksize = 1024 * 1024

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(blksize), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest().startswith(hash_prefix.strip().lower())
