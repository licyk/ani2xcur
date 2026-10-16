"""Xcursor 与 Windows 光标格式写入工具。"""

from __future__ import annotations

import struct
from io import BytesIO

from PIL import Image

from ani2xcur.config import LOGGER_COLOR, LOGGER_LEVEL, LOGGER_NAME
from ani2xcur.cursor_conversion.native_cursor.models import CursorFrame, CursorImage
from ani2xcur.cursor_conversion.native_cursor.parsers import (
    ANIH_HEADER,
    CHUNK_HEADER,
    ICON_DIR,
    ICON_DIR_ENTRY,
    RIFF_HEADER,
    UNSIGNED,
    XCURSOR_FILE_HEADER,
    XCURSOR_IMAGE_HEADER,
    XCURSOR_IMAGE_TYPE,
    XCURSOR_MAGIC,
    XCURSOR_TOC_CHUNK,
    XCURSOR_VERSION,
)
from ani2xcur.logger import get_logger

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)

ANI_ICON_FLAG = 0x1
WINDOWS_ANIMATED_STANDARD_SIZE = 32
WINDOWS_HIGH_RES_SIZE = 96


def to_xcursor(frames: list[CursorFrame]) -> bytes:
    """将光标帧序列化为 Xcursor 文件内容。

    Args:
        frames (list[CursorFrame]): 要写入的光标帧列表。
    Returns:
        bytes: Xcursor 文件的二进制内容。
    Raises:
        ValueError: 图像尺寸或热点坐标不符合 Xcursor 格式要求时抛出。
    """
    chunks: list[tuple[int, int, bytes]] = []
    for frame in frames:
        for cursor in frame.images:
            image = cursor.image.convert("RGBA")
            width, height = image.size
            hotspot_x, hotspot_y = cursor.hotspot
            if width > 0x7FFF or height > 0x7FFF:
                raise ValueError(f"Xcursor image is too large: {width}x{height}")
            if not 0 <= hotspot_x <= width or not 0 <= hotspot_y <= height:
                raise ValueError(f"Cursor hotspot is outside the image: {cursor.hotspot}")

            header = XCURSOR_IMAGE_HEADER.pack(
                XCURSOR_IMAGE_HEADER.size,
                XCURSOR_IMAGE_TYPE,
                cursor.nominal,
                1,
                width,
                height,
                hotspot_x,
                hotspot_y,
                round(frame.delay * 1000),
            )
            chunks.append((XCURSOR_IMAGE_TYPE, cursor.nominal, header + _premultiply_rgba_to_bgra(image.tobytes())))
    logger.debug(
        "序列化 Xcursor 文件: frame_count=%s, chunk_count=%s, nominal_sizes=%s",
        len(frames),
        len(chunks),
        sorted({chunk_subtype for _, chunk_subtype, _ in chunks}),
    )

    header = XCURSOR_FILE_HEADER.pack(
        XCURSOR_MAGIC,
        XCURSOR_FILE_HEADER.size,
        XCURSOR_VERSION,
        len(chunks),
    )

    offset = XCURSOR_FILE_HEADER.size + len(chunks) * XCURSOR_TOC_CHUNK.size
    toc: list[bytes] = []
    for chunk_type, chunk_subtype, chunk in chunks:
        toc.append(XCURSOR_TOC_CHUNK.pack(chunk_type, chunk_subtype, offset))
        offset += len(chunk)

    return b"".join([header, *toc, *(chunk for _, _, chunk in chunks)])


def to_cur(frame: CursorFrame) -> bytes:
    """将静态光标帧序列化为 Windows .cur 文件内容。

    Args:
        frame (CursorFrame): 要写入的静态光标帧。
    Returns:
        bytes: .cur 文件的二进制内容。
    Raises:
        ValueError: 图像尺寸或热点坐标不符合 .cur 格式要求时抛出。
    """
    return _to_cur(frame, animated_frame=False)


def _to_cur(frame: CursorFrame, *, animated_frame: bool) -> bytes:
    images = _select_windows_cursor_images(frame.images, animated_frame=animated_frame)
    header = ICON_DIR.pack(0, 2, len(images))
    directory: list[bytes] = []
    image_data: list[bytes] = []
    offset = ICON_DIR.size + len(images) * ICON_DIR_ENTRY.size

    for cursor in images:
        image = cursor.image.convert("RGBA")
        width, height = image.size
        if width > 256 or height > 256:
            raise ValueError(f"Image too big for CUR format: {width}x{height}")
        hotspot_x, hotspot_y = cursor.hotspot
        if not 0 <= hotspot_x <= width or not 0 <= hotspot_y <= height:
            raise ValueError(f"Cursor hotspot is outside the image: {cursor.hotspot}")

        payload = _image_to_dib(image) if animated_frame or _is_high_res_cursor_image(cursor) else _image_to_png(image)
        image_data.append(payload)
        directory.append(
            ICON_DIR_ENTRY.pack(
                0 if width == 256 else width,
                0 if height == 256 else height,
                0,
                0,
                hotspot_x,
                hotspot_y,
                len(payload),
                offset,
            )
        )
        offset += len(payload)

    logger.debug("序列化 CUR 文件: image_count=%s", len(images))
    return b"".join([header, *directory, *image_data])


def to_ani(frames: list[CursorFrame]) -> bytes:
    """将动画光标帧序列化为 Windows .ani 文件内容。

    Args:
        frames (list[CursorFrame]): 要写入的动画光标帧列表。
    Returns:
        bytes: .ani 文件的二进制内容。
    """
    rates = [_frame_delay_to_jiffies(frame.delay, animated=len(frames) > 1) for frame in frames]
    ani_header = ANIH_HEADER.pack(
        ANIH_HEADER.size,
        len(frames),
        len(frames),
        0,
        0,
        32,
        1,
        1,
        ANI_ICON_FLAG,
    )

    cursor_list = _ani_cursor_list(frames)
    rate_chunk = CHUNK_HEADER.pack(b"rate", UNSIGNED.size * len(rates)) + b"".join(UNSIGNED.pack(rate) for rate in rates)
    body = b"".join(
        [
            CHUNK_HEADER.pack(b"anih", len(ani_header)),
            ani_header,
            RIFF_HEADER.pack(b"LIST", len(cursor_list) + 4, b"fram"),
            cursor_list,
            rate_chunk,
        ]
    )
    logger.debug("序列化 ANI 文件: frame_count=%s, rates=%s", len(frames), rates)
    return RIFF_HEADER.pack(b"RIFF", len(body) + 4, b"ACON") + body


def to_smart(frames: list[CursorFrame]) -> tuple[str, bytes]:
    """根据帧数量自动选择 .cur 或 .ani 输出格式。

    Args:
        frames (list[CursorFrame]): 要写入的光标帧列表。
    Returns:
        tuple[str, bytes]: 输出扩展名和对应的二进制内容。
    """
    if len(frames) == 1:
        logger.debug("自动选择 Windows 光标输出格式: .cur")
        return ".cur", to_cur(frames[0])
    logger.debug("自动选择 Windows 光标输出格式: .ani")
    return ".ani", to_ani(frames)


def _image_to_png(image: Image.Image) -> bytes:
    rgba_image = image.convert("RGBA")
    if _is_grayscale_rgba(rgba_image):
        rgba_image = rgba_image.convert("LA")

    buffer = BytesIO()
    rgba_image.save(buffer, format="PNG")
    return buffer.getvalue()


def _ani_cursor_list(frames: list[CursorFrame]) -> bytes:
    chunks: list[bytes] = []
    for frame in frames:
        cur_file = _to_cur(frame, animated_frame=True)
        chunk = CHUNK_HEADER.pack(b"icon", len(cur_file)) + cur_file
        if len(cur_file) & 1:
            chunk += b"\0"
        chunks.append(chunk)
    return b"".join(chunks)


def _frame_delay_to_jiffies(delay: float, animated: bool) -> int:
    jiffies = round(delay * 60)
    if animated and jiffies <= 0:
        return 1
    return jiffies


def _select_windows_cursor_images(images: list[CursorImage], *, animated_frame: bool) -> list[CursorImage]:
    sorted_images = sorted(images, key=lambda cursor: (cursor.nominal, cursor.image.width, cursor.image.height))
    high_res_images = [cursor for cursor in sorted_images if _is_high_res_cursor_image(cursor)]
    if animated_frame:
        if not high_res_images:
            return [_select_windows_animated_image(sorted_images)]
        return [max(high_res_images, key=lambda cursor: (cursor.nominal, cursor.image.width, cursor.image.height))]
    if not high_res_images:
        return sorted_images
    return [cursor for cursor in sorted_images if cursor.nominal >= WINDOWS_HIGH_RES_SIZE or _is_high_res_cursor_image(cursor)]


def _select_windows_animated_image(images: list[CursorImage]) -> CursorImage:
    return min(
        images,
        key=lambda cursor: (
            abs(cursor.nominal - WINDOWS_ANIMATED_STANDARD_SIZE),
            abs(max(cursor.image.size) - WINDOWS_ANIMATED_STANDARD_SIZE),
            cursor.nominal,
        ),
    )


def _is_high_res_cursor_image(cursor: CursorImage) -> bool:
    width, height = cursor.image.size
    return max(width, height, cursor.nominal) > WINDOWS_HIGH_RES_SIZE


def _is_grayscale_rgba(image: Image.Image) -> bool:
    pixels = image.convert("RGBA").tobytes()
    for index in range(0, len(pixels), 4):
        red = pixels[index]
        green = pixels[index + 1]
        blue = pixels[index + 2]
        if red != green or red != blue:
            return False
    return True


def _image_to_dib(image: Image.Image) -> bytes:
    rgba_image = image.convert("RGBA")
    width, height = rgba_image.size
    pixels = rgba_image.tobytes()
    row_stride = width * 4
    mask_stride = ((width + 31) // 32) * 4

    xor_rows: list[bytes] = []
    mask_rows: list[bytes] = []
    for y in range(height - 1, -1, -1):
        xor_row = bytearray(row_stride)
        mask_row = bytearray(mask_stride)
        for x in range(width):
            src = (y * width + x) * 4
            dst = x * 4
            red, green, blue, alpha = pixels[src : src + 4]
            if alpha == 0:
                red = green = blue = 0
            xor_row[dst : dst + 4] = bytes((blue, green, red, alpha))
            if alpha == 0:
                mask_row[x // 8] |= 0x80 >> (x % 8)
        xor_rows.append(bytes(xor_row))
        mask_rows.append(bytes(mask_row))

    xor_bitmap = b"".join(xor_rows)
    mask_bitmap = b"".join(mask_rows)
    header = struct.pack("<IiiHHIIiiII", 40, width, height * 2, 1, 32, 0, len(xor_bitmap) + len(mask_bitmap), 0, 0, 0, 0)
    return header + xor_bitmap + mask_bitmap


def _premultiply_rgba_to_bgra(source: bytes) -> bytes:
    result = bytearray(len(source))
    for index in range(0, len(source), 4):
        red = source[index]
        green = source[index + 1]
        blue = source[index + 2]
        alpha = source[index + 3]
        if alpha < 255:
            red = (red * alpha + 127) // 255
            green = (green * alpha + 127) // 255
            blue = (blue * alpha + 127) // 255
        result[index : index + 4] = bytes((blue, green, red, alpha))
    return bytes(result)
