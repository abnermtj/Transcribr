"""
Helpers to transcribe mp3 to srt
"""

import whisper
from typing import Iterator


def format_timestamp(
    seconds: float, always_include_hours: bool = False, decimal_marker: str = "."
):
    """
    Formats timestamps to one suitable for srt files
    """
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return (
        f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"
    )


def to_srt(transcript: Iterator[dict]):
    """
    Convert a transcript to a string in SRT format
    """
    out = ""

    for i, segment in enumerate(transcript, start=1):
        out += f"{i}\n"
        out += f"{format_timestamp(segment['start'], True, ',')} --> "
        out += f"{format_timestamp(segment['end'], True, ',')}\n"
        out += f"{segment['text'].strip().replace('-->', '->')}\n"

    return out


def scribe(model, input_lang, audio_path):
    """
    Transcribes the model and returns a string for the srt subtitle file
    """
    if input_lang != "Auto":
        # make log-Mel spectrogram and move to the same device as the model
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)

        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        options = whisper.DecodingOptions(fp16=False, language=input_lang)

        result = whisper.decode(model, mel, options)
    else:
        result = model.transcribe(audio_path)
    return to_srt(result["segments"])
