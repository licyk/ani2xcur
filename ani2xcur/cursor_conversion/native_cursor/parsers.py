"""基于 Pillow 的光标文件解析器。"""

from __future__ import annotations

import struct
from collections import defaultdict
from io import BytesIO
from typing import Iterable

from PIL import Image

from ani2xcur.config import LOGGER_COLOR, LOGGER_LEVEL, LOGGER_NAME
from ani2xcur.cursor_conversion.native_cursor.models import CursorFrame, CursorImage
from ani2xcur.logger import get_logger

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)

CUR_MAGIC = b"\x00\x00\x02\x00"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
XCURSOR_MAGIC = b"Xcur"
XCURSOR_VERSION = 0x00010000
XCURSOR_IMAGE_TYPE = 0xFFFD0002
WINDOWS_ANIMATED_STANDARD_SIZE = 32

ICON_DIR = struct.Struct("<HHH")
ICON_DIR_ENTRY = struct.Struct("<BBBBHHII")
RIFF_HEADER = struct.Struct("<4sI4s")
CHUNK_HEADER = struct.Struct("<4sI")
ANIH_HEADER = struct.Struct("<IIIIIIIII")
UNSIGNED = struct.Struct("<I")
XCURSOR_FILE_HEADER = struct.Struct("<4sIII")
XCURSOR_TOC_CHUNK = struct.Struct("<III")
XCURSOR_IMAGE_HEADER = struct.Struct("<IIIIIIIII")

ANI_ICON_FLAG = 0x1


def parse_blob(blob: bytes) -> list[CursorFrame]:
    """解析 Windows CUR/ANI 或 Linux Xcursor 文件内容。

    Args:
        blob (bytes): 光标文件的二进制内容。
    Returns:
        list[CursorFrame]: 解析得到的光标帧列表。
    Raises:
        ValueError: 光标文件格式不受支持或文件内容损坏时抛出。
    """
    if blob.startswith(CUR_MAGIC):
        logger.debug("识别到 Windows CUR 光标文件")
        return parse_cur(blob)
    if _is_ani(blob):
        logger.debug("识别到 Windows ANI 光标文件")
        return parse_ani(blob)
    if blob.startswith(XCURSOR_MAGIC):
        logger.debug("识别到 Xcursor 光标文件")
        return parse_xcursor(blob)
    raise ValueError("Unsupported cursor file format")


def parse_cur(blob: bytes) -> list[CursorFrame]:
    """将 Windows .cur 文件解析为静态光标帧。

    Args:
        blob (bytes): .cur 文件的二进制内容。
    Returns:
        list[CursorFrame]: 仅包含一个静态帧的光标帧列表。
    Raises:
        ValueError: .cur 文件内容损坏或格式不受支持时抛出。
    """
    if len(blob) < ICON_DIR.size:
        raise ValueError("CUR file is too small")

    reserved, cursor_type, image_count = ICON_DIR.unpack_from(blob, 0)
    if reserved != 0 or cursor_type != 2:
        raise ValueError("Not a CUR file")
    if image_count <= 0:
        raise ValueError("CUR file does not contain images")
    logger.debug("解析 CUR 文件: image_count=%s", image_count)

    entries_start = ICON_DIR.size
    entries_end = entries_start + image_count * ICON_DIR_ENTRY.size
    if len(blob) < entries_end:
        raise ValueError("CUR directory is truncated")

    images: list[CursorImage] = []
    offset = entries_start
    for _ in range(image_count):
        width_byte, height_byte, _, _, hotspot_x, hotspot_y, image_size, image_offset = ICON_DIR_ENTRY.unpack_from(blob, offset)
        offset += ICON_DIR_ENTRY.size

        if image_offset + image_size > len(blob):
            raise ValueError("CUR image payload is truncated")

        entry_width = 256 if width_byte == 0 else width_byte
        entry_height = 256 if height_byte == 0 else height_byte
        payload = blob[image_offset : image_offset + image_size]
        image = _decode_cur_payload(payload, entry_width, entry_height)
        images.append(
            CursorImage(
                image=image,
                hotspot=(hotspot_x, hotspot_y),
                nominal=image.width,
            )
        )

    logger.debug("CUR 文件解析完成: sizes=%s", [image.image.size for image in images])
    return [CursorFrame(images=images)]


def parse_ani(blob: bytes) -> list[CursorFrame]:
    """解析基于 icon 帧的 Windows .ani 文件。

    Args:
        blob (bytes): .ani 文件的二进制内容。
    Returns:
        list[CursorFrame]: 按动画顺序排列的光标帧列表。
    Raises:
        ValueError: .ani 文件内容损坏或格式不受支持时抛出。
        NotImplementedError: .ani 文件使用暂不支持的原始 BMP 帧时抛出。
    """
    if not _is_ani(blob):
        raise ValueError("Not an ANI file")

    _, riff_size, _ = RIFF_HEADER.unpack_from(blob, 0)
    riff_end = min(len(blob), 8 + riff_size)
    offset = RIFF_HEADER.size

    frame_count = 0
    step_count = 0
    display_rate = 1
    flags = 0
    icon_frames: list[CursorFrame] = []
    order: list[int] | None = None
    delays: list[int] | None = None

    for name, size, payload_start, payload_end in _iter_chunks(blob, offset, riff_end):
        if name == b"anih":
            if size != ANIH_HEADER.size:
                raise ValueError(f"Unexpected anih header size {size}")
            header_size, frame_count, step_count, _, _, _, _, display_rate, flags = ANIH_HEADER.unpack_from(blob, payload_start)
            if header_size != ANIH_HEADER.size:
                raise ValueError(f"Unexpected size in anih header {header_size}")
            if not flags & ANI_ICON_FLAG:
                raise NotImplementedError("Raw BMP ANI frames are not supported")
        elif name == b"LIST" and blob[payload_start : payload_start + 4] == b"fram":
            for child_name, child_size, child_start, _ in _iter_chunks(blob, payload_start + 4, payload_end):
                if child_name != b"icon":
                    continue
                icon_frames.append(parse_cur(blob[child_start : child_start + child_size])[0])
        elif name == b"seq ":
            order = [value for (value,) in UNSIGNED.iter_unpack(blob[payload_start:payload_end])]
        elif name == b"rate":
            delays = [value for (value,) in UNSIGNED.iter_unpack(blob[payload_start:payload_end])]

    if not icon_frames:
        raise ValueError("ANI file does not contain icon frames")

    frame_count = frame_count or len(icon_frames)
    step_count = step_count or frame_count
    has_order_chunk = order is not None
    has_delay_chunk = delays is not None
    order = list(range(frame_count)) if order is None else order
    delays = [display_rate for _ in range(step_count)] if delays is None else delays

    if len(order) != step_count:
        raise ValueError(f"Wrong animation sequence size: {len(order)}, expected {step_count}")
    if len(delays) != step_count:
        raise ValueError(f"Wrong animation rate size: {len(delays)}, expected {step_count}")

    logger.debug(
        "解析 ANI 文件: frame_count=%s, step_count=%s, icon_frames=%s, has_seq=%s, has_rate=%s",
        frame_count,
        step_count,
        len(icon_frames),
        has_order_chunk,
        has_delay_chunk,
    )
    sequence: list[CursorFrame] = []
    for frame_index, delay in zip(order, delays):
        if frame_index >= len(icon_frames):
            raise ValueError(f"ANI sequence references missing frame {frame_index}")
        frame = icon_frames[frame_index].clone()
        frame.delay = delay / 60
        sequence.append(frame)

    logger.debug("ANI 文件解析完成: sequence_frames=%s", len(sequence))
    return sequence


def parse_xcursor(blob: bytes) -> list[CursorFrame]:
    """解析 Xcursor 文件。

    Args:
        blob (bytes): Xcursor 文件的二进制内容。
    Returns:
        list[CursorFrame]: 解析得到的光标帧列表。
    Raises:
        ValueError: Xcursor 文件内容损坏或格式不受支持时抛出。
    """
    sequences = _parse_xcursor_size_sequences(blob)
    ordered_sizes = sorted(sequences)
    frame_counts = {nominal: len(sequences[nominal]) for nominal in ordered_sizes}
    logger.debug("Xcursor 文件尺寸序列: %s", frame_counts)

    if _xcursor_sequences_share_timeline(sequences):
        frames = _combine_xcursor_size_sequences(sequences)
        logger.debug("Xcursor 尺寸序列共享时间轴，保留多尺寸帧")
    else:
        selected_size = min(
            ordered_sizes,
            key=lambda nominal: (abs(nominal - WINDOWS_ANIMATED_STANDARD_SIZE), nominal),
        )
        frames = sequences[selected_size]
        logger.debug(
            "Xcursor 尺寸序列具有独立时间轴，选择最接近 Windows 标准动画尺寸的序列: selected=%s, target=%s",
            selected_size,
            WINDOWS_ANIMATED_STANDARD_SIZE,
        )

    logger.debug("Xcursor 文件解析完成: frame_count=%s", len(frames))
    return frames


def _parse_xcursor_size_sequences(blob: bytes) -> dict[int, list[CursorFrame]]:
    """按名义尺寸解析彼此独立的 Xcursor 动画序列。"""
    if len(blob) < XCURSOR_FILE_HEADER.size:
        raise ValueError("Xcursor file is too small")

    magic, _, version, toc_size = XCURSOR_FILE_HEADER.unpack_from(blob, 0)
    if magic != XCURSOR_MAGIC:
        raise ValueError("Not an Xcursor file")
    if version != XCURSOR_VERSION:
        raise ValueError(f"Unsupported Xcursor version 0x{version:08x}")

    toc_end = XCURSOR_FILE_HEADER.size + toc_size * XCURSOR_TOC_CHUNK.size
    if len(blob) < toc_end:
        raise ValueError("Xcursor table of contents is truncated")

    chunks: list[tuple[int, int, int]] = []
    offset = XCURSOR_FILE_HEADER.size
    for _ in range(toc_size):
        chunks.append(XCURSOR_TOC_CHUNK.unpack_from(blob, offset))
        offset += XCURSOR_TOC_CHUNK.size
    logger.debug("解析 Xcursor 文件: toc_size=%s", toc_size)

    images_by_size: dict[int, list[CursorFrame]] = defaultdict(list)
    for chunk_type, chunk_subtype, position in chunks:
        if chunk_type != XCURSOR_IMAGE_TYPE:
            continue
        if position + XCURSOR_IMAGE_HEADER.size > len(blob):
            raise ValueError("Xcursor image header is truncated")

        header_size, actual_type, nominal, _, width, height, hotspot_x, hotspot_y, delay = XCURSOR_IMAGE_HEADER.unpack_from(blob, position)
        if header_size != XCURSOR_IMAGE_HEADER.size:
            raise ValueError(f"Unexpected Xcursor image header size {header_size}")
        if actual_type != chunk_type or nominal != chunk_subtype:
            raise ValueError("Xcursor image chunk does not match table of contents")
        if width > 0x7FFF or height > 0x7FFF:
            raise ValueError(f"Xcursor image is too large: {width}x{height}")
        if hotspot_x > width or hotspot_y > height:
            raise ValueError("Xcursor hotspot is outside the image")

        image_start = position + XCURSOR_IMAGE_HEADER.size
        image_size = width * height * 4
        image_end = image_start + image_size
        if image_end > len(blob):
            raise ValueError("Xcursor pixel data is truncated")

        rgba = _unpremultiply_bgra_to_rgba(blob[image_start:image_end])
        image = Image.frombytes("RGBA", (width, height), rgba)
        images_by_size[nominal].append(
            CursorFrame(
                images=[CursorImage(image=image, hotspot=(hotspot_x, hotspot_y), nominal=nominal)],
                delay=delay / 1000,
            )
        )

    if not images_by_size:
        raise ValueError("Xcursor file does not contain images")
    return dict(images_by_size)


def _xcursor_sequences_share_timeline(sequences: dict[int, list[CursorFrame]]) -> bool:
    """判断不同尺寸序列能否无损合并为多尺寸动画帧。"""
    frame_counts = {len(frames) for frames in sequences.values()}
    if len(frame_counts) != 1:
        return False

    frame_count = next(iter(frame_counts))
    if frame_count == 1:
        return True

    delay_sequences = {tuple(frame.delay for frame in frames) for frames in sequences.values()}
    return len(delay_sequences) == 1


def _combine_xcursor_size_sequences(sequences: dict[int, list[CursorFrame]]) -> list[CursorFrame]:
    """将共享时间轴的尺寸序列合并为多尺寸动画帧。"""
    ordered_sequences = [sequences[nominal] for nominal in sorted(sequences)]
    combined: list[CursorFrame] = []
    for frame_items in zip(*ordered_sequences):
        combined.append(
            CursorFrame(
                images=[frame.images[0] for frame in frame_items],
                delay=frame_items[0].delay,
            )
        )
    return combined


def _is_ani(blob: bytes) -> bool:
    if len(blob) < RIFF_HEADER.size:
        return False
    signature, _, subtype = RIFF_HEADER.unpack_from(blob, 0)
    return signature == b"RIFF" and subtype == b"ACON"


def _iter_chunks(blob: bytes, offset: int, end: int) -> Iterable[tuple[bytes, int, int, int]]:
    while offset + CHUNK_HEADER.size <= end:
        name, size = CHUNK_HEADER.unpack_from(blob, offset)
        payload_start = offset + CHUNK_HEADER.size
        payload_end = payload_start + size
        if payload_end > end:
            raise ValueError(f"Chunk {name!r} is truncated")
        yield name, size, payload_start, payload_end
        offset = payload_end + (payload_end & 1)


def _decode_cur_payload(payload: bytes, entry_width: int, entry_height: int) -> Image.Image:
    if payload.startswith(PNG_MAGIC):
        with Image.open(BytesIO(payload)) as image:
            return image.convert("RGBA").copy()
    return _decode_dib_payload(payload, entry_width, entry_height)


def _decode_dib_payload(payload: bytes, entry_width: int, entry_height: int) -> Image.Image:
    if len(payload) < 40:
        raise ValueError("DIB cursor payload is too small")

    header_size = struct.unpack_from("<I", payload, 0)[0]
    if header_size < 40 or len(payload) < header_size:
        raise ValueError(f"Unsupported DIB header size {header_size}")

    width, raw_height, planes, bit_count, compression, image_size, _, _, colors_used, _ = struct.unpack_from("<iiHHIIiiII", payload, 4)
    if planes != 1:
        raise ValueError(f"Unsupported DIB plane count {planes}")
    if compression != 0:
        raise ValueError(f"Unsupported compressed DIB cursor payload {compression}")
    if bit_count not in {1, 4, 8, 24, 32}:
        raise ValueError(f"Unsupported DIB cursor bit depth {bit_count}")

    width = abs(width) or entry_width
    absolute_height = abs(raw_height)
    if width <= 0 or absolute_height <= 0:
        raise ValueError("Invalid DIB cursor dimensions")

    palette: list[tuple[int, int, int]] = []
    color_table_size = 0
    if bit_count <= 8:
        color_table_entries = colors_used or (1 << bit_count)
        color_table_size = color_table_entries * 4
        color_table_end = header_size + color_table_size
        if len(payload) < color_table_end:
            raise ValueError("DIB cursor color table is truncated")
        for color_offset in range(header_size, color_table_end, 4):
            b, g, r, _ = payload[color_offset : color_offset + 4]
            palette.append((r, g, b))
    pixel_offset = header_size + color_table_size
    row_stride = ((width * bit_count + 31) // 32) * 4
    mask_stride = ((width + 31) // 32) * 4
    available_data_size = len(payload) - pixel_offset
    declared_data_size = image_size or available_data_size
    height = _infer_dib_cursor_height(
        absolute_height=absolute_height,
        entry_height=entry_height,
        row_stride=row_stride,
        mask_stride=mask_stride,
        available_data_size=available_data_size,
        declared_data_size=declared_data_size,
    )
    xor_size = row_stride * height
    mask_offset = pixel_offset + xor_size
    if len(payload) < pixel_offset + xor_size:
        raise ValueError("DIB cursor pixel data is truncated")

    has_mask = len(payload) >= mask_offset + mask_stride * height
    bottom_up = raw_height > 0
    rgba = bytearray(width * height * 4)

    alpha_values: list[int] = []
    if bit_count == 32:
        for row in range(height):
            row_start = pixel_offset + row * row_stride
            alpha_values.extend(payload[row_start + 3 : row_start + width * 4 : 4])
    use_alpha_channel = any(alpha > 0 for alpha in alpha_values)

    for y in range(height):
        source_y = height - 1 - y if bottom_up else y
        source_row = pixel_offset + source_y * row_stride
        mask_row = mask_offset + source_y * mask_stride
        for x in range(width):
            dst = (y * width + x) * 4
            if bit_count == 32:
                src = source_row + x * 4
                b, g, r, a = payload[src : src + 4]
                alpha = a if use_alpha_channel else 255
            elif bit_count == 24:
                src = source_row + x * 3
                b, g, r = payload[src : src + 3]
                alpha = 255
            else:
                palette_index = _decode_indexed_dib_pixel(payload, source_row, x, bit_count)
                if palette_index >= len(palette):
                    raise ValueError(f"DIB cursor palette index {palette_index} is out of range")
                r, g, b = palette[palette_index]
                alpha = 255

            if has_mask:
                mask_byte = payload[mask_row + x // 8]
                if mask_byte & (0x80 >> (x % 8)):
                    alpha = 0

            rgba[dst : dst + 4] = bytes((r, g, b, alpha))

    return Image.frombytes("RGBA", (width, height), bytes(rgba))


def _infer_dib_cursor_height(
    *,
    absolute_height: int,
    entry_height: int,
    row_stride: int,
    mask_stride: int,
    available_data_size: int,
    declared_data_size: int,
) -> int:
    """Infer the real bitmap height for cursor DIB payloads.

    CUR directory dimensions are limited to a byte and can disagree with the
    embedded DIB header. Cursor DIBs normally store XOR and AND bitmaps, so the
    header height is twice the visible image height.
    """

    def exact_with_mask(height: int) -> bool:
        return row_stride * height + mask_stride * height == declared_data_size

    def exact_without_mask(height: int) -> bool:
        return row_stride * height == declared_data_size

    def fits_with_mask(height: int) -> bool:
        return row_stride * height + mask_stride * height <= available_data_size

    def fits_without_mask(height: int) -> bool:
        return row_stride * height <= available_data_size

    candidate_heights: list[int] = []
    if absolute_height % 2 == 0:
        candidate_heights.append(absolute_height // 2)
    candidate_heights.append(absolute_height)
    if entry_height > 0:
        candidate_heights.append(entry_height)

    for height in candidate_heights:
        if height > 0 and (exact_with_mask(height) or exact_without_mask(height)):
            return height

    for height in candidate_heights:
        if height > 0 and (fits_with_mask(height) or fits_without_mask(height)):
            return height

    raise ValueError("DIB cursor pixel data is truncated")


def _decode_indexed_dib_pixel(payload: bytes, row_start: int, x: int, bit_count: int) -> int:
    if bit_count == 8:
        return payload[row_start + x]
    if bit_count == 4:
        byte = payload[row_start + x // 2]
        if x % 2 == 0:
            return byte >> 4
        return byte & 0x0F
    if bit_count == 1:
        byte = payload[row_start + x // 8]
        return 1 if byte & (0x80 >> (x % 8)) else 0
    raise ValueError(f"Unsupported indexed DIB cursor bit depth {bit_count}")


def _unpremultiply_bgra_to_rgba(source: bytes) -> bytes:
    result = bytearray(len(source))
    for index in range(0, len(source), 4):
        blue = source[index]
        green = source[index + 1]
        red = source[index + 2]
        alpha = source[index + 3]
        if alpha == 0:
            red = green = blue = 0
        elif alpha < 255:
            red = min(255, (red * 255 + alpha // 2) // alpha)
            green = min(255, (green * 255 + alpha // 2) // alpha)
            blue = min(255, (blue * 255 + alpha // 2) // alpha)
        result[index : index + 4] = bytes((red, green, blue, alpha))
    return bytes(result)
