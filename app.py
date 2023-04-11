from pathlib import Path
import tempfile
import streamlit as st
from dotenv import load_dotenv
import datetime
from model import create_index, load_index, run_query


@st.cache_data
def add_to_chat_history(user_input, bot_response):
    st.session_state.chat_history.append({"role": "user", "text": user_input, "time": datetime.datetime.now()})
    st.session_state.chat_history.append({"role": "bot", "text": bot_response, "time": datetime.datetime.now()})


def write_chat_content(container):
    chat_display = ""
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            chat_display += f"##### {message['time'].strftime('%Y-%m-%d %H:%M:%S')} - You:\n\n"
            chat_display += f"{message['text']}\n\n"
        else:
            chat_display += f"##### {message['time'].strftime('%Y-%m-%d %H:%M:%S')} - Bot:\n\n"
            chat_display += f"{message['text']}\n\n"

    container.markdown(chat_display, unsafe_allow_html=True)


def main():
    # Load environment variables
    load_dotenv()

    st.title("Chat with PDF")

    if "index" not in st.session_state:
        st.session_state.index = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    pdf_or_index_file = st.sidebar.file_uploader("PDF or Index JSON", type=["pdf", "json"])
    if pdf_or_index_file is not None:
        with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
            Path(tmp_file.name).write_bytes(pdf_or_index_file.read())
            if pdf_or_index_file.type == "application/pdf":
                index = create_index(tmp_file.name)
                index.save_to_disk("index.json")
                st.session_state.index = index
            else:
                st.session_state.index = load_index(tmp_file.name)

    if st.session_state.index is not None:
        # チャット履歴を表示するコンテナ
        chat_container = st.empty()
        write_chat_content(chat_container)  # 答えを待ってる間にチャット履歴が表示されないと不便なので、ここでも表示を行う

        # テキスト入力と送信ボタン
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask anything.")
            send_button = st.form_submit_button("Send")

            if send_button and user_input:
                bot_response = run_query(st.session_state.index, user_input, 2)
                add_to_chat_history(user_input, bot_response)

            write_chat_content(chat_container)  # 答えを追加して表示


if __name__ == "__main__":
    main()
