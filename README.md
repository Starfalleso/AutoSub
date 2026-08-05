<img width="1001" height="727" alt="autosub" src="https://github.com/user-attachments/assets/a003ba97-edb7-41ed-9f16-5e9794ec4dff" />
# AutoSub

AI-powered subtitle generator for desktop. Drop in an audio/video file and
AutoSub transcribes it locally using Whisper models via `faster-whisper`, then
lets you preview and export the result as SRT, VTT, or plain text.

![Waveform icon](assets/app_icon.svg)
<img width="1001" height="727" alt="autosub" src="https://github.com/user-attachments/assets/a003ba97-edb7-41ed-9f16-5e9794ec4dff" />

## Features

- **Drag & drop** or browse for audio/video files (MP4, MKV, MP3, WAV, FLAC, …)
- **Local transcription** with `faster-whisper` — no cloud, files stay on your machine
- **Model selection** (tiny → large-v3) for speed / accuracy tradeoffs
- **Automatic language detection** or a manual language choice (30 languages)
- **Configurable compute type** (`int8` is the safe CPU default)
- **Export formats**: SRT, WebVTT, or plain text
- **Dark UI** with a waveform icon and gradient accents
- Pre-built `.exe` available — no Python install needed

## Pre-built exe

Download `AutoSub.exe` from the [releases page](https://github.com/Starfalleso/AutoSub/releases)
or build it yourself (see below). The exe bundles everything except the Whisper
model weights, which are downloaded once on first use and cached locally.

## Requirements

- Python 3.14
- Dependencies are managed with [`uv`](https://docs.astral.sh/uv/)

## Setup

```sh
uv sync
```

## Usage

```sh
uv run python main.py
```

Select a file, choose a model (large-v3-turbo is a good default), then click
**Generate Subtitles**. When it finishes, the preview fills in and you can
choose an export format (SRT / VTT / TXT) and click **Export Subtitles**.

## Building the exe

```sh
uv run pyinstaller AutoSub.spec --noconfirm
```

The output is `dist/AutoSub.exe`. The spec file bundles the waveform icon and
sets `console=False` so no terminal window appears.

## Project layout

```
main.py                entry point
paths.py               resource path helper (dev + PyInstaller)
core/
  transcriber.py       faster-whisper wrapper
  subtitle.py          SRT / VTT / TXT building & saving
ui/
  main_window.py       PyQt6 UI, worker thread, handlers
  styles.py            dark stylesheet + accent color
assets/
  app_icon.svg         waveform SVG icon
  app_icon.ico         Windows icon (generated from SVG)
```

## Notes

- No NVIDIA GPU assumed — `int8` on CPU is the default compute type.
- Transcription runs on a background `QThread` so the UI stays responsive.
- Whisper model weights are downloaded from HuggingFace Hub on first use and
  cached in `~/.cache/huggingface/hub/`.
