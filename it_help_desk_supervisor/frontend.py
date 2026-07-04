import uuid
import requests
import streamlit as st

API_URL = "http://localhost:8001/chat"

st.set_page_config(
    page_title="IT Help Desk",
    page_icon="🖥️",
)

st.title("🖥️ IT Help Desk Assistant")

# ------------------------------------------------------------------
# Session State
# ------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------

with st.sidebar:
    st.header("Conversation")

    st.caption("Thread ID")
    st.code(st.session_state.thread_id)

    if st.button("🆕 New Conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# ------------------------------------------------------------------
# Chat History
# ------------------------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ------------------------------------------------------------------
# Chat Input
# ------------------------------------------------------------------

if prompt := st.chat_input("Describe your problem..."):

    # Display user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Call FastAPI
    with st.spinner("Thinking..."):

        try:
            response = requests.post(
                API_URL,
                json={
                    "message": prompt,
                    "thread_id": st.session_state.thread_id,
                },
                timeout=60,
            )

            response.raise_for_status()

            answer = response.json()["response"]

        except requests.exceptions.RequestException as e:
            answer = f"❌ Error contacting the API:\n\n{e}"

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)