import streamlit as st
import requests
import os
import json

st.set_page_config(
    page_title="Speech-to-Text Transcription App", page_icon="👄", layout="wide"
)

import whisper
import os
from typing import Iterator, TextIO
    
model = whisper.load_model("small")

def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"


def write_srt(transcript: Iterator[dict]):
    """
    Write a transcript to a file in SRT format.
    Example usage:
        from pathlib import Path
        from whisper.utils import write_srt
        result = transcribe(model, audio_path, temperature=temperature, **args)
        # save SRT
        audio_basename = Path(audio_path).stem
        with open(Path(output_dir) / (audio_basename + ".srt"), "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt)
    """
    out = ""
    for i, segment in enumerate(transcript, start=1):
        # write srt lines
        out +=      f"{i}\n"
        out += f"{format_timestamp(segment['start'], always_include_hours=True, decimal_marker=',')} --> "
        out += f"{format_timestamp(segment['end'], always_include_hours=True, decimal_marker=',')}\n"
        out += f"{segment['text'].strip().replace('-->', '->')}\n"
    return out

def scribe(audio_path):
    # load audio and pad/trim it to fit 30 seconds
    result = model.transcribe(audio_path)
    print(result)
    # audio = whisper.load_audio(audio_path)
    # audio = whisper.pad_or_trim(audio)

    # # make log-Mel spectrogram and move to the same device as the model
    # mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # # detect the spoken language
    # _, probs = model.detect_language(mel)
    # print(f"Detected language: {max(probs, key=probs.get)}")

    # # decode the audio
    # options = whisper.DecodingOptions(fp16 = False)
    # result = whisper.decode(model, mel, options)

    # # audio_basename = os.path.basename(audio_path)
    # # save SRT
    # # with open(os.path.join(output_dir, audio_basename + ".srt"), "w", encoding="utf-8") as srt:
    # print(audio)
    # print(audio_path)
    with open(os.path.join(audio_path + ".srt"), "w", encoding="utf-8") as srt:
        return write_srt(result["segments"], file=srt)

def _max_width_():
    max_width_str = f"max-width: 1200px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

_max_width_()
st.image("logo.png", width=350)

def main():
    pages = {
        "👾 Free mode (2MB per API call)": Free_mode,
        "🤗 Full mode": Full_mode,
    }

    if "page" not in st.session_state:
        st.session_state.update(
            {
                # Default page
                "page": "Home",
            }
        )

    with st.sidebar:
        page = st.radio("Select your mode", tuple(pages.keys()))

    pages[page]()


def Free_mode():
    f = st.file_uploader("", type=[".mp3"])
    print(f)
    st.info(
                f"""
                        👆 Upload a .wav file. Or try a sample: [Wav sample 01](https://github.com/CharlyWargnier/CSVHub/blob/main/Wave_files_demos/Welcome.wav?raw=true) | [Wav sample 02](https://github.com/CharlyWargnier/CSVHub/blob/main/Wave_files_demos/The_National_Park.wav?raw=true)
                        """
            )

    text_value = ""
    if f is not None:
        path_in = f.name
        old_file_position = f.tell()
        f.seek(0, os.SEEK_END)
        getsize = f.tell()  # os.path.getsize(path_in)
        f.seek(old_file_position, os.SEEK_SET)
        getsize = round((getsize / 1000000), 1)
        st.caption("The size of this file is: " + str(getsize) + "MB")

        if getsize < 2:  # File more than 2MB
            st.success("OK, less than 1 MB")
        else:
            st.error("More than 1 MB! Please use your own API")
            st.stop()
        text_value =  scribe(path_in)

    if text_value:
        # Print the output to your Streamlit app
        st.success(text_value)

        st.download_button(
        "Download the transcription",
        text_value,
        file_name=None,
        mime=None,
        key=None,
        help=None,
        on_click=None,
        args=None,
        kwargs=None,
)
    # ADD CODE FOR DEMO HERE

def Full_mode():
    f = st.file_uploader("", type=[".wav"])
    st.info(
                f"""
                        👆 Upload a .wav file. Or try a sample: [Wav sample 01](https://github.com/CharlyWargnier/CSVHub/blob/main/Wave_files_demos/Welcome.wav?raw=true) | [Wav sample 02](https://github.com/CharlyWargnier/CSVHub/blob/main/Wave_files_demos/The_National_Park.wav?raw=true)
                        """
            )
    # ADD CODE FOR API KEY MODE HERE

if __name__ == '__main__':
    main()