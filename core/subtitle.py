def format_timestamp(seconds: float) -> str:
    """Convert a float number of seconds into an SRT timestamp (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def segments_to_srt(segments: list) -> str:
    """Build the full SRT text from a list of whisper segments.

    Each segment is a dict: {"start": float, "end": float, "text": str}.
    """
    srt_content = []
    for i, segment in enumerate(segments, 1):
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = segment["text"].strip()
        srt_content.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(srt_content)


def save_srt(segments: list, output_path: str) -> None:
    """Write the segments to a .srt file at the given path (UTF-8)."""
    srt_content = segments_to_srt(segments)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
