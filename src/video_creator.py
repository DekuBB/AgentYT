from __future__ import annotations

import textwrap
from pathlib import Path

from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _prepare_frame(image_path: Path, title: str, frame_path: Path, size: tuple[int, int] = (1280, 720)) -> Path:
    img = Image.open(image_path).convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", size, (8, 11, 18))
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 455, size[0], size[1]), fill=(0, 0, 0, 155))

    font = _font(42)
    wrapped = textwrap.fill(title, width=34)
    draw.multiline_text((60, 500), wrapped, fill=(255, 255, 255, 255), font=font, spacing=10)

    composed = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    frame_path.parent.mkdir(parents=True, exist_ok=True)
    composed.save(frame_path, quality=92)
    return frame_path


def create_video(audio_path: Path, image_paths: list[Path], title: str, output_path: Path) -> Path:
    if not image_paths:
        raise RuntimeError("Brak obrazow do montazu wideo")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    audio = AudioFileClip(str(audio_path))
    per_clip = max(4.0, audio.duration / len(image_paths))
    clips = []

    frame_dir = output_path.parent / "frames"
    for index, image_path in enumerate(image_paths, start=1):
        frame_path = _prepare_frame(image_path, title, frame_dir / f"frame_{index}.jpg")
        clips.append(ImageClip(str(frame_path)).set_duration(per_clip))

    video = concatenate_videoclips(clips, method="compose").set_duration(audio.duration).set_audio(audio)
    video.write_videofile(
        str(output_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=2,
        logger=None,
    )
    audio.close()
    video.close()
    for clip in clips:
        clip.close()
    return output_path
