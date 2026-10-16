"""光标转换使用的 Pillow 图像变换工具。"""

from __future__ import annotations

from math import ceil

from PIL import Image, ImageColor, ImageFilter

from ani2xcur.config import LOGGER_COLOR, LOGGER_LEVEL, LOGGER_NAME
from ani2xcur.cursor_conversion.native_cursor.models import CursorFrame, CursorImage
from ani2xcur.logger import get_logger

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)

DEFAULT_XCURSOR_SIZES = (24, 28, 32, 40, 48, 56, 64, 72, 80, 88, 96)
"""转换到 Linux Xcursor 主题时默认生成的名义尺寸列表。"""


def scale_frames(frames: list[CursorFrame], scale: float) -> None:
    """原地缩放每个光标图像和热点坐标。

    Args:
        frames (list[CursorFrame]): 要缩放的光标帧列表。
        scale (float): 缩放倍率。
    Raises:
        ValueError: 缩放倍率小于或等于 0 时抛出。
    """
    if scale <= 0:
        raise ValueError("Cursor scale must be greater than zero")

    logger.debug("开始缩放光标帧: frame_count=%s, scale=%s", len(frames), scale)
    for frame in frames:
        for cursor in frame.images:
            width, height = cursor.image.size
            new_size = (
                max(1, round(width * scale)),
                max(1, round(height * scale)),
            )
            cursor.image = cursor.image.convert("RGBA").resize(new_size, Image.Resampling.LANCZOS)
            hotspot_x, hotspot_y = cursor.hotspot
            cursor.hotspot = (
                max(0, round(hotspot_x * scale)),
                max(0, round(hotspot_y * scale)),
            )
    logger.debug("光标帧缩放完成")


def normalize_xcursor_sizes(
    frames: list[CursorFrame],
    target_sizes: list[int] | tuple[int, ...],
) -> None:
    """原地补齐 Xcursor 文件需要提供的名义尺寸。

    Args:
        frames (list[CursorFrame]): 要补齐尺寸的光标帧列表。
        target_sizes (list[int] | tuple[int, ...]): 目标名义尺寸列表。
    Raises:
        ValueError: 目标尺寸为空或包含非法值时抛出。
    """
    sizes = sorted(set(target_sizes))
    if not sizes:
        raise ValueError("Xcursor size list must not be empty")
    if any(size <= 0 for size in sizes):
        raise ValueError("Xcursor sizes must be greater than zero")

    generated_count = 0
    reused_count = 0
    for frame in frames:
        if not frame.images:
            continue

        existing_by_nominal = {cursor.nominal: cursor for cursor in frame.images}
        normalized_images: list[CursorImage] = []
        normalized_sizes = sorted(set(sizes) | set(existing_by_nominal))
        for target_size in normalized_sizes:
            if target_size in existing_by_nominal:
                normalized_images.append(existing_by_nominal[target_size])
                reused_count += 1
                continue

            source = _nearest_cursor_image(frame.images, target_size)
            normalized_images.append(_resize_cursor_image(source, target_size))
            generated_count += 1

        frame.images = normalized_images
    logger.debug(
        "Xcursor 尺寸补齐完成: frame_count=%s, target_sizes=%s, reused=%s, generated=%s",
        len(frames),
        sizes,
        reused_count,
        generated_count,
    )


def add_shadow_to_frames(
    frames: list[CursorFrame],
    *,
    color: str,
    opacity: int,
    radius: float,
    sigma: float,
    xoffset: float,
    yoffset: float,
) -> None:
    """为每个光标图像原地添加近似 Windows 风格的阴影。

    Args:
        frames (list[CursorFrame]): 要添加阴影的光标帧列表。
        color (str): 阴影颜色。
        opacity (int): 阴影不透明度。
        radius (float): 阴影半径比例。
        sigma (float): 阴影模糊比例。
        xoffset (float): 阴影水平偏移比例。
        yoffset (float): 阴影垂直偏移比例。
    """
    opacity = max(0, min(255, opacity))
    logger.debug(
        "开始添加光标阴影: frame_count=%s, color=%s, opacity=%s, radius=%s, sigma=%s, xoffset=%s, yoffset=%s",
        len(frames),
        color,
        opacity,
        radius,
        sigma,
        xoffset,
        yoffset,
    )
    for frame in frames:
        for cursor in frame.images:
            image, hotspot = _add_shadow_to_image(
                cursor.image,
                cursor.hotspot,
                color=color,
                opacity=opacity,
                radius=radius,
                sigma=sigma,
                xoffset=xoffset,
                yoffset=yoffset,
            )
            cursor.image = image
            cursor.hotspot = hotspot
    logger.debug("光标阴影添加完成")


def _add_shadow_to_image(
    source: Image.Image,
    hotspot: tuple[int, int],
    *,
    color: str,
    opacity: int,
    radius: float,
    sigma: float,
    xoffset: float,
    yoffset: float,
) -> tuple[Image.Image, tuple[int, int]]:
    image = source.convert("RGBA")
    width, height = image.size
    offset_x = round(xoffset * width)
    offset_y = round(yoffset * height)
    blur_radius = max(radius * width, sigma * width, 0)
    margin = ceil(blur_radius * 2)

    left_pad = margin + max(0, -offset_x)
    top_pad = margin + max(0, -offset_y)
    right_pad = margin + max(0, offset_x)
    bottom_pad = margin + max(0, offset_y)
    canvas_size = (width + left_pad + right_pad, height + top_pad + bottom_pad)

    alpha = image.getchannel("A")
    shadow_alpha = Image.new("L", canvas_size, 0)
    shadow_alpha.paste(alpha, (left_pad + offset_x, top_pad + offset_y))
    if blur_radius > 0:
        shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(blur_radius))
    if opacity < 255:
        shadow_alpha = shadow_alpha.point(lambda value: value * opacity // 255)

    color_values = ImageColor.getrgb(color)
    red, green, blue = color_values[0], color_values[1], color_values[2]
    shadow = Image.new("RGBA", canvas_size, (red, green, blue, 0))
    shadow.putalpha(shadow_alpha)

    result = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    result.alpha_composite(shadow)
    result.alpha_composite(image, dest=(left_pad, top_pad))

    bbox = result.getbbox()
    if bbox is None:
        return image, hotspot

    cropped = result.crop(bbox)
    hotspot_x = hotspot[0] + left_pad - bbox[0]
    hotspot_y = hotspot[1] + top_pad - bbox[1]
    hotspot_x = max(0, min(cropped.width, hotspot_x))
    hotspot_y = max(0, min(cropped.height, hotspot_y))
    return cropped, (hotspot_x, hotspot_y)


def _nearest_cursor_image(
    images: list[CursorImage],
    target_size: int,
) -> CursorImage:
    return min(images, key=lambda image: (abs(image.nominal - target_size), -image.nominal))


def _resize_cursor_image(
    source: CursorImage,
    target_size: int,
) -> CursorImage:
    image = source.image.convert("RGBA")
    width, height = image.size
    source_nominal = source.nominal if source.nominal > 0 else max(width, height)
    scale = target_size / source_nominal
    new_size = (
        max(1, round(width * scale)),
        max(1, round(height * scale)),
    )
    hotspot_x, hotspot_y = source.hotspot
    new_hotspot = (
        max(0, min(new_size[0], round(hotspot_x * scale))),
        max(0, min(new_size[1], round(hotspot_y * scale))),
    )
    return CursorImage(
        image=image.resize(new_size, Image.Resampling.LANCZOS),
        hotspot=new_hotspot,
        nominal=target_size,
    )
