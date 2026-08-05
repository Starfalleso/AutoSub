# AutoSub

AI-powered subtitle generator for desktop. Drop in an audio/video file and
AutoSub transcribes it locally using Whisper models via `faster-whisper`, then
lets you preview and export the result as an SRT file.

## Features

- Drag & drop or browse for audio/video files (MP4, MKV, MP3, WAV, FLAC, …)
- Local transcription with `faster-whisper` — no cloud, files stay on your machine
- Model selection (tiny → large-v3) for speed / accuracy tradeoffs
- Automatic language detection or a manual language choice
- Configurable compute type (`int8` is the safe CPU default)
- Live progress bar with elapsed / total time
- In-app preview of the generated SRT, then one-click export

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
**Generate Subtitles**. When it finishes, the preview fills in and **Export
SRT** becomes available.

## Project layout

```
main.py               entry point
core/
  transcriber.py      faster-whisper wrapper
  subtitle.py         SRT building / saving
ui/
  main_window.py      PyQt6 UI, worker thread, handlers
  styles.py           dark stylesheet + accent color
```

## Notes

- No NVIDIA GPU assumed — `int8` on CPU is the default compute type.
- Transcription runs on a background `QThread` so the UI stays responsive.
