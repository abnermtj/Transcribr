import streamlit as st
import os
import whisper
import os
from typing import Iterator
from pydub import AudioSegment
import shutil

model = whisper.load_model("small")

st.set_page_config(
    page_title="Transcibr", page_icon="🧊", layout="wide"
)

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


def to_srt(transcript: Iterator[dict]):
    """
    Convert a transcript to a string in SRT format 
    """
    out = ""
    for i, segment in enumerate(transcript, start=1):
        out +=      f"{i}\n"
        out += f"{format_timestamp(segment['start'], always_include_hours=True, decimal_marker=',')} --> "
        out += f"{format_timestamp(segment['end'], always_include_hours=True, decimal_marker=',')}\n"
        out += f"{segment['text'].strip().replace('-->', '->')}\n"

    return out

def scribe(audio_path):
    result = model.transcribe(audio_path)
    return to_srt(result["segments"])

def _max_width_():
    max_width_str = f"max-width: 1600px;"
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


def main():
    _max_width_()
    st.image("assets/logo.png", width=350)

    pages = {
        "Transcribe": transcribe_process,
        "History": history_process,
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

def transcribe_process():
    uploader_file_list = st.file_uploader("Upload Audio and Video files to transcribe", type=['mkv', 'mp4','avi','wav', 'mp3'], accept_multiple_files=True)
    st.info(
            f"""
            👆 Upload Multiple Audio or Video files 
            """
            )

    for uploaded_file in uploader_file_list:
        text_value = ""
        if uploaded_file is not None:
            file_name = uploaded_file.name
            input_file_path = 'input/' + uploaded_file.name
            pre, ext = os.path.splitext(file_name)
            output_file_path = './output/' + pre + ".mp3"

            with open(input_file_path, mode='wb') as save:
                save.write(uploaded_file.read()) # save video to disk
                audio = AudioSegment.from_file(input_file_path)
                audio.export(output_file_path, format="mp3")

            file_size = get_file_size(uploaded_file)
            st.caption("Working On " + file_name + "(" + str(file_size) + " MB)")

            text_value =  scribe(output_file_path)
            if text_value:
                col1, col2 = st.columns(2)

                col1.success(file_name + " is done")

                col2.download_button(
                "Download .srt",
                text_value,
                file_name= pre + '.srt',
                mime=None,
                key=None,
                help=None,
                on_click=None,
                args=None,
                kwargs=None,
                )
            else:
                st.error(
                f"""
                No subtitles found.
                """
                )

    shutil.make_archive('all', 'zip', 'output')

    expander = st.expander("History")
    with expander:
        with open('all.zip', mode='rb') as archive:
                st.download_button(
                        label="Download all",
                        data = archive,
                        file_name= 'all.zip',
                        mime=None,
                        key=None,
                        help=None,
                        on_click=None,
                        args=None,
                        kwargs=None,
                )
                pass

def get_file_size(f):
    old_file_position = f.tell()
    f.seek(0, os.SEEK_END)
    getsize = f.tell()  
    f.seek(old_file_position, os.SEEK_SET)
    return round((getsize / 1000000), 1)

def history_process():
    st.info(
                f"""
                        File history
                        """
            )
    st.header("TITLE")

if __name__ == '__main__':
    main()