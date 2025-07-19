# Audio Download & Transcribe Toolkit

A lightweight tooling set that lets you **download the best‑quality audio** from YouTube/BiliBili and feed it directly to OpenAI Whisper for transcription – all configurable via a single YAML file.

---

## 1  Prerequisites

| Requirement     | Why you need it           | Quick check                     |
| --------------- | ------------------------- | ------------------------------- |
| Python ≥ 3.8    | Run the toolkit           | `python --version`              |
| ffmpeg (binary) | Audio demux ⇢ WAV/PCM     | `ffmpeg -version`               |
| yt‑dlp          | Grab streams from the web | Installed by `requirements.txt` |
| PyYAML          | Parse `config.yaml`       | Installed by `requirements.txt` |

```bash
# Clone / download this repo, then:
python -m venv env && ./env/Scripts/activate        # Windows example
pip install -r requirements.txt
```

---

## 2  Configuration

All knobs live in \`\`. Example:

```yaml
ffmpeg_path: "C:/Tools/ffmpeg/bin/ffmpeg.exe"   # Absolute or keep just "ffmpeg" if added to PATH
output_dir: "./downloads"                      # Where converted files land

audio:
  preferredcodec: "mp3"                        # mp3 / wav / flac / m4a…
  preferredquality: "192"                     # kbps; MP3 caps at 320
```

> ✱ Leave `preferredquality` blank to stick with the default **192 kbps** – or bump it, e.g. `256`.

---

## 3  CLI usage

### 3.1  Download audio only

```bash
python -m src.utils.download <URL> [options]
```

| Flag                         | Description                    | Default              |
| ---------------------------- | ------------------------------ | -------------------- |
| `-o DIR`, `--output-dir DIR` | Where to save the file         | `output_dir` in YAML |
| `-c CODEC`, `--codec CODEC`  | Target codec (`mp3`, `wav`, …) | `preferredcodec`     |
| `-q N`, `--quality N`        | Bit‑rate (kbps)                | `preferredquality`   |
| `--overwrite`                | Replace existing files         | *False*              |

**Example** – grab Rick Astley at 256 kbps MP3:

```bash
python -m src.utils.download https://www.youtube.com/watch?v=oxyPTZ83IIE -q 256
```

> You may omit `-q` to stick with 192 kbps (or whatever YAML says).

### 3.2  Transcribe (coming soon)

```bash
python -m scripts.transcribe input.mp4 --lang fr --output srt
```

---

## 4  Library usage

```python
from src.utils.download import download_audio_from_url

url = "https://www.bilibili.com/video/BV1kW411j7cH"
path = download_audio_from_url(url, quality="320")
print("Saved to", path)
```

---

## 5  Troubleshooting

| Symptom                                       | Fix                                                                       |
| --------------------------------------------- | ------------------------------------------------------------------------- |
| `ffmpeg binary not found …`                   | Check `ffmpeg_path` or add *bin* dir to system `PATH`.                    |
| Got `.webm` not `.mp3`                        | Source stream lacked separate audio; add `--codec mp3`.                   |
| Whisper returns English text for French audio | Pass `language="fr"` to `model.transcribe()`, or trim loud ambient intro. |

---

## 6  Supported sites

`yt‑dlp` inherits hundreds of extractors from youtube‑dl. Any site whose video/playlist extractor is labelled “✅ *working*” can be passed to this toolkit, and the audio stream will be pulled automatically. Below is not exhaustive, just the crowd‑pleasers:

| Category     | Examples (audio supported)                                         |
| ------------ | ------------------------------------------------------------------ |
| Major video  | YouTube, BiliBili, Vimeo, Dailymotion, TikTok                      |
| Music        | SoundCloud, Bandcamp, Mixcloud                                     |
| Social media | Twitter / X, Instagram, Facebook, Reddit video, Snapchat Spotlight |
| Streaming TV | Twitch VODs & Clips, Arte, FranceTV, BBC iPlayer (needs cookies)   |
| Podcasts     | Apple Podcasts, Podbean, Spotify RSS\*                             |
| Education    | Coursera, Udemy, MIT OpenCourseWare                                |

> ℹ️ For the full, constantly‑updated list, run `yt-dlp --list-extractors` or check the official repo: [https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).
>
> \* Spotify requires a public RSS feed (e.g. podcasts). Music tracks need a login cookie.

---

## 7  Roadmap

-

