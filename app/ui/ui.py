import streamlit as st
import requests

API_URL = "http://localhost:8000/generate"  # your FastAPI endpoint


# -----------------------------------------------------
# STREAMLIT CONFIG
# -----------------------------------------------------

st.set_page_config(
    page_title="Harri Engineering Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("Harri Dev Team AI Assistant")



# -----------------------------------------------------
# SESSION STATE
# -----------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "debug_info" not in st.session_state:
    st.session_state.debug_info = None


# -----------------------------------------------------
# SIDEBAR (DEBUG PANEL)
# -----------------------------------------------------

with st.sidebar:
    st.header("🛠 Debug Panel")

    if not st.session_state.debug_info:
        st.info("No debug data yet.")
    else:
        st.subheader("Intents")
        st.json(st.session_state.debug_info.get("intents"))

        st.subheader("Retrievals")
        st.json(st.session_state.debug_info.get("retrievals"))

        st.subheader("Raw LLM Output")
        st.json(st.session_state.debug_info.get("raw_llm"))

        st.subheader("Built Prompt")
        st.code(st.session_state.debug_info.get("prompt"), language="markdown")

    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.debug_info = None
        st.rerun()


# -----------------------------------------------------
# RENDER CHAT HISTORY
# -----------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # show citations under assistant message
        if msg["role"] == "assistant" and msg.get("citations"):
            st.markdown("**References:**")
            for c in msg["citations"]:
                if c.get("section"):
                    st.markdown(f"- `{c['source']} — {c['section']}`")
                else:
                    st.markdown(f"- `{c['source']}`")


# -----------------------------------------------------
# USER INPUT
# -----------------------------------------------------

user_query = st.chat_input("Ask something about Harri engineering...")

if user_query:
    # Store user message
    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )

    # Show user bubble
    with st.chat_message("user"):
        st.markdown(user_query)

    # -----------------------------------------------------
    # CALL FASTAPI BACKEND
    # -----------------------------------------------------
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:
                response = requests.post(
                    API_URL,
                    json={"query": user_query},
                    timeout=60
                )
            except Exception as e:
                st.error(f"❌ Failed to contact backend: {e}")
                st.stop()

            if response.status_code != 200:
                st.error(f"❌ Backend error: {response.text}")
                st.stop()

            data = response.json()

            # LLMResponseModel
            llm_block = data.get("llm", {})

            answer = llm_block.get("answer", "No answer returned from backend.")
            citations = llm_block.get("citations", [])

            # -----------------------------------------------------
            # RENDER ANSWER
            # -----------------------------------------------------
            st.markdown(answer)

            if citations:
                st.markdown("**References:**")
                for c in citations:
                    if c.get("section"):
                        st.markdown(f"- `{c['source']} — {c['section']}`")
                    else:
                        st.markdown(f"- `{c['source']}`")

    # Save assistant message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "citations": citations
        }
    )

    # debug data if you return them from backend
    st.session_state.debug_info = {
        "intents": data.get("intents"),
        "probabilities": data.get("probabilities"),
        "retrievals": data.get("retrievals"),
        "raw_llm": data.get("llm"),
    }

    st.rerun()
