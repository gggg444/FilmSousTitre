from __future__ import annotations

"""src/utils/download.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions for downloading the *best* audio track from
an online video (YouTube, BiliBili, etc.) and converting it to the
preferred codec using **yt_dlp** and **ffmpeg**.

The module respects the central ``config/config.yaml`` file so that
*no* hard‑coded paths live in your business logic.

Example
-------
```python
from src.utils.download import download_audio_from_url

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
audio_path = download_audio_from_url(url)
print("Saved to", audio_path)
```
"""

from pathlib import Path
from typing import Optional
import shutil

import yt_dlp

from .config import get_config

__all__ = ["download_audio_from_url"]


class FFMpegNotFoundError(RuntimeError):
    """Raised when ffmpeg binary specified in the config does not exist."""


def _resolve_ffmpeg_path() -> str:
    ffmpeg_path = get_config("ffmpeg_path")
    if not ffmpeg_path:
        raise FFMpegNotFoundError("'ffmpeg_path' not set in config.yaml. Please provide the absolute "
            "path to the ffmpeg executable.")

    p = Path(ffmpeg_path).expanduser()
    if p.exists():
        return str(p)

    from_path = shutil.which(ffmpeg_path)
    if from_path:
        return from_path

    raise FFMpegNotFoundError(f"ffmpeg binary not found: {ffmpeg_path}")

def download_audio_from_url(
    url: str,
    *,
    output_dir: Optional[str] = None,
    codec: Optional[str] = None,
    quality: Optional[str] = None,
    overwrite: bool = False,
) -> Path:
    """Download the best‑available audio stream from *url*.

    Parameters
    ----------
    url : str
        The video URL to download.
    output_dir : str | None, default = value from config.yml
        Directory where the resulting audio file will be placed.
    codec : str | None, default = value from config.yml
        Target audio codec (e.g. "mp3", "m4a", "wav").
    quality : str | None, default = value from config.yml
        Target bitrate (in kbps) understood by ffmpeg (e.g. "192").
    overwrite : bool, default = False
        If *True*, existing files with the same name are overwritten.

    Returns
    -------
    pathlib.Path
        The path to the downloaded (and converted) audio file.
    """

    # ---- 1. Resolve config values ------------------------------------------
    ffmpeg_path = _resolve_ffmpeg_path()

    out_dir = Path(output_dir or get_config("output_dir", "./downloads")).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    codec = codec or get_config("audio.preferredcodec", "mp3")
    quality = quality or get_config("audio.preferredquality", "192")

    # ---- 2. Build yt_dlp options -------------------------------------------
    ydl_opts: dict = {
        "outtmpl": str(out_dir / "%(title)s.%(ext)s"),
        "format": "bestaudio",
        "ffmpeg_location": ffmpeg_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec,
                "preferredquality": quality,
            }
        ],
        # yt_dlp >=2024.4.9 supports overwrites option; fallback handled below
        "overwrites": overwrite,
    }

    # ---- 3. Download + convert ---------------------------------------------
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        original_file = Path(ydl.prepare_filename(info_dict))

    # yt_dlp converts in‑place: the extension changes after post‑processing
    final_file = original_file.with_suffix(f".{codec}")

    # Sometimes yt_dlp returns temp names; ensure the expected file exists
    if not final_file.exists():
        # yt_dlp may append codec to title; fall back to searching directory
        candidates = list(original_file.parent.glob(f"*{info_dict['id']}*.{codec}"))
        if candidates:
            final_file = candidates[0]
        else:
            raise FileNotFoundError(
                "Download finished but output file not found. "
                "Check yt_dlp logs or your post‑processor settings."
            )

    return final_file


# ---------------------------------------------------------------------------
# Optional CLI: ``python -m src.utils.download <url>``
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Download best audio from a video URL.")
    parser.add_argument("url", help="Video URL to download.")
    parser.add_argument("--output-dir", "-o", help="Directory to save audio.")
    parser.add_argument("--codec", "-c", help="Target codec (mp3, wav, etc.).")
    parser.add_argument("--quality", "-q", help="Bitrate, e.g. 192.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args()

    try:
        path = download_audio_from_url(
            args.url,
            output_dir=args.output_dir,
            codec=args.codec,
            quality=args.quality,
            overwrite=args.overwrite,
        )
        print(f"\n✔ Download complete: {path}")
    except Exception as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        sys.exit(1)
