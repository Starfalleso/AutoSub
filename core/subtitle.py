def format_timestamp_srt(seconds: float) -> str:
    """Convert seconds to an SRT timestamp (HH:MM:SS,mmm — comma millis)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Convert seconds to a VTT timestamp (HH:MM:SS.mmm — dot millis)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def segments_to_srt(segments: list) -> str:
    """Build SRT text. Each segment: {"start": float, "end": float, "text": str}."""
    blocks = []
    for i, segment in enumerate(segments, 1):
        start = format_timestamp_srt(segment["start"])
        end = format_timestamp_srt(segment["end"])
        text = segment["text"].strip()
        blocks.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(blocks)


def segments_to_vtt(segments: list) -> str:
    """Build WebVTT text (WEBVTT header, no cue numbers)."""
    blocks = ["WEBVTT\n"]
    for segment in segments:
        start = format_timestamp_vtt(segment["start"])
        end = format_timestamp_vtt(segment["end"])
        text = segment["text"].strip()
        blocks.append(f"{start} --> {end}\n{text}\n")
    return "\n".join(blocks)


def segments_to_txt(segments: list) -> str:
    """Build a plain text transcript (no timestamps)."""
    return "\n".join(segment["text"].strip() for segment in segments if segment["text"].strip())


def save(segments: list, output_path: str, fmt: str = "srt") -> None:
    """Write segments to a file in srt/vtt/txt format (UTF-8)."""
    fmt = (fmt or "srt").lower()
    if fmt == "vtt":
        content = segments_to_vtt(segments)
    elif fmt == "txt":
        content = segments_to_txt(segments)
    else:
        content = segments_to_srt(segments)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def save_srt(segments: list, output_path: str) -> None:
    """Convenience wrapper for saving SRT."""
    save(segments, output_path, "srt")
