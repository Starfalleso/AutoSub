from faster_whisper import WhisperModel


class Transcriber:
    """Thin wrapper around faster-whisper.

    Handles model loading and converting the streamed result into plain
    Python dicts so the UI layer never touches whisper internals.
    """

    def __init__(self, model_size: str = "base", device: str = "auto", compute_type: str = "auto"):
        self.model_size = model_size    # e.g. "tiny", "base", "small", "medium", "large-v3-turbo"
        self.device = device            # "auto", "cpu", "cuda"
        self.compute_type = compute_type  # "auto", "int8", "float16", "float32"
        self.model = None               # lazy-loaded WhisperModel

    def load_model(self, progress_callback=None):
        """Instantiate the Whisper model once (no-op if already loaded)."""
        if self.model is not None:
            return

        # Fall back to int8 (best CPU performance) when the caller asks for auto.
        if self.compute_type == "auto":
            self.compute_type = "int8"

        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type
        )

    def transcribe(self, audio_path: str, language: str = None, progress_callback=None) -> list:
        """Transcribe an audio/video file.

        Returns a tuple: (segments, detected_language, duration_seconds).
        Each segment is a dict: {"start": float, "end": float, "text": str}.
        progress_callback, if given, is called with (current_seconds, total_seconds, language).
        """
        if self.model is None:
            self.load_model()

        # "Auto" (or None) means let whisper detect the language automatically.
        segments_iter, info = self.model.transcribe(
            audio_path,
            language=language if language and language != "auto" else None,
            beam_size=5,
            vad_filter=True,   # skip silent sections for cleaner output
        )

        detected_language = info.language
        duration = info.duration

        # Materialize the lazy stream into a list of plain dicts,
        # reporting progress as each segment completes.
        segments = []
        for segment in segments_iter:
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
            })
            if progress_callback:
                progress_callback(segment.end, duration, detected_language)

        return segments, detected_language, duration
