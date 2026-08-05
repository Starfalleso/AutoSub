# AGENTS.md

Guidance for working in this repository.

## Project overview

**AutoSub** is a desktop app (PyQt6) that generates subtitles from audio/video
files using local Whisper models via `faster-whisper`. The user has **no NVIDIA
GPU**, so the default compute type is `int8` on CPU.

## Layout

- `main.py` — entry point; creates `QApplication` and shows `MainWindow`.
- `ui/main_window.py` — all UI: layout, drag & drop, worker thread, handlers.
- `ui/styles.py` — global Qt stylesheet (`MODERN_DARK`) + `ACCENT` color.
- `core/transcriber.py` — thin wrapper around `faster_whisper.WhisperModel`.
- `core/subtitle.py` — builds/ saves SRT text from whisper segments.

## Conventions

- Python 3.14, deps managed with `uv` (see `uv.lock`, `pyproject.toml`).
- Theming is **ultra-dark + indigo accent** (`#6366f1`). UI must match the
  existing aesthetic — keep the two-pane layout (left controls / right preview).
- Widgets are styled by object name in the stylesheet (e.g. `#card`,
  `#generateBtn`). Keep new styled widgets registered there.
- `segments` are plain dicts: `{"start": float, "end": float, "text": str}`.

## Commands

- Run the app: `uv run python main.py`
- Smoke-test that the UI imports/launches:
  `uv run python -c "import sys; from PyQt6.QtWidgets import QApplication; from ui.main_window import MainWindow; app=QApplication(sys.argv); w=MainWindow(); w.show(); app.processEvents(); print('OK')"`

## Gotchas

- QSS has no `box-shadow`; use `QGraphicsDropShadowEffect` for shadows.
- Keep transcription on the worker `QThread` — never block the UI thread.
- Do not add comments to code unless the user explicitly asks (they already
  asked once; the codebase is already commented).
