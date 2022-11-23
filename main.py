"""
Hosts a web app that transcribes media
"""

import os
import shutil
import pandas as pd
import whisper
import whisper.tokenizer as whisper_tok
from pydub import AudioSegment
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from mutagen.mp3 import MP3
from transcribe import scribe
from utils import get_file_size, get_pretty_date, get_pretty_duration

INPUT_DIR = "input"
OUTPUT_DIR = "output"

model = whisper.load_model("small")


st.set_page_config(
    page_title="Transcibr", page_icon="🧊", layout="wide"
)  # Always ontop of main.py


def _max_width_():
    max_width_str = "max-width: 1600px;"
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
    """
    Entry point
    """
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
        page = st.radio("", tuple(pages.keys()))

    pages[page]()


def aggrid_interactive_table(data_frame: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.
    Args:
        data_frame: Source dataframe
    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        data_frame, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        data_frame,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="balham",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection


def transcribe_process():
    """
    Process for transcribe page
    """

    Languages = list(whisper_tok.LANGUAGES.values())
    Languages.insert(0, "Auto")
    input_lang = st.selectbox("Input language", Languages)

    uploader_file_list = st.file_uploader(
        "Upload Audio and Video files to transcribe",
        type=["mkv", "mp4", "avi", "wav", "mp3"],
        accept_multiple_files=True,
    )
    st.info(
        """
        👆 Upload Multiple Audio or Video files
        """
    )

    for uploaded_file in uploader_file_list:
        if uploaded_file is not None:
            cap = st.caption("Processing")

            file_name, pre, output_file_path, file_size = process_file(uploaded_file)

            cap.caption(
                body=("Transcribing " + file_name + "(" + str(file_size) + " MB)")
            )

            text_value = scribe(model, input_lang, output_file_path)
            with open("output/" + pre + ".srt", "w") as text_file:
                text_file.write(text_value)

            if text_value:
                col1, col2 = st.columns(2)
                col1.success(file_name + " is done")
                col2.download_button(
                    "Download .srt",
                    text_value,
                    file_name=pre + ".srt",
                    mime=None,
                    key=None,
                    help=None,
                    on_click=None,
                    args=None,
                    kwargs=None,
                )
            else:
                st.error(
                    """
                No subtitles found.
                """
                )


def process_file(uploaded_file):
    """
    Saves the file to disk and converts it to mp3. Relevant file features extracted and returned
    """
    file_name = uploaded_file.name
    input_file_path = "input/" + uploaded_file.name
    filename_no_extension, _ = os.path.splitext(file_name)
    output_file_path = "output/" + filename_no_extension + ".mp3"

    with open(input_file_path, mode="wb") as save:
        save.write(uploaded_file.read())  # save video to disk
        audio = AudioSegment.from_file(input_file_path)
        audio.export(output_file_path, format="mp3")

    file_size = get_file_size(uploaded_file)
    return file_name, filename_no_extension, output_file_path, file_size


def history_process():
    """
    Process for the history page
    """
    st.info(
        """
        File history
        """
    )
    shutil.make_archive("all", "zip", "output")

    with open("all.zip", mode="rb") as archive:
        st.download_button(
            label="Download all srt",
            data=archive,
            file_name="all.zip",
            mime=None,
            key=None,
            help=None,
            on_click=None,
            args=None,
            kwargs=None,
        )

    file_data_list = []
    for file in os.listdir("output"):
        if file.endswith(".mp3"):
            file_data = {
                "name": file,
                "date": get_pretty_date(os.path.getmtime("output/" + file)),
                "duration": get_pretty_duration(MP3("output/" + file).info.length),
            }
            file_data_list.append(file_data)
    file_data_list = pd.DataFrame(file_data_list)

    selection = aggrid_interactive_table(data_frame=file_data_list)
    if selection["selected_rows"]:
        select_data = selection["selected_rows"][0]
        st.write("Selected: " + select_data["name"])

        # Get srt file
        pre, _ = os.path.splitext(select_data["name"])
        with open("output/" + pre + ".srt") as file:
            text_value = file.read()

        st.download_button(
            "Download .srt",
            text_value,
            file_name=pre + ".srt",
            mime=None,
            key=None,
            help=None,
            on_click=None,
            args=None,
            kwargs=None,
        )


if __name__ == "__main__":
    main()
