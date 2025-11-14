import streamlit as st
import requests

API_URL = "http://localhost:8000/generate"  


# -----------------------------------------------------
# STREAMLIT CONFIG
# -----------------------------------------------------

st.set_page_config(
    page_title="Harri Assistant",
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

        st.subheader("Probabilities ")
        st.json(st.session_state.debug_info.get("probabilities"))

        st.subheader("Retrievals")
        st.json(st.session_state.debug_info.get("retrievals"))

        st.subheader("Raw LLM Output")
        st.json(st.session_state.debug_info.get("raw_llm"))


    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.debug_info = None
        st.rerun()
    
    


# -----------------------------------------------------
# RENDER CHAT HISTORY
# -----------------------------------------------------

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("citations"):
            st.markdown("**References:**")
            for c in msg["citations"]:
                if c.get("section"):
                    st.markdown(f"- `{c['source']} — {c['section']}`")
                else:
                    st.markdown(f"- `{c['source']}`")

        # ----------------------------
        # CLEAN FEEDBACK UI
        # ----------------------------
        if msg["role"] == "assistant":

            st.markdown(
                """
                <div style="margin-top: -10px; margin-bottom: 8px; font-weight: 600; font-size: 16px;">
                    Was this helpful?
                </div>
                """,
                unsafe_allow_html=True
            )

            # Inline button layout
            c1, c2, _ = st.columns([1,1,8])

            yes_clicked = c1.button("👍 Yes", key=f"fb_yes_{i}")
            no_clicked = c2.button("👎 No", key=f"fb_no_{i}")

            # YES → send minimal feedback
            if yes_clicked:
                requests.post(
                    "http://localhost:8000/feedback",
                    json={
                        "query": st.session_state.messages[i - 1]["content"],
                        "answer": msg["content"],
                        "helpful": True,
                        "details": None
                    }
                )
                st.success("Thanks! Your feedback was recorded.")

            # NO → reveal text box & submit button inline (clean)
            if no_clicked:
                reason = st.text_area("What went wrong?", key=f"fb_reason_{i}")

                if st.button("Submit Feedback", key=f"fb_submit_{i}"):
                    requests.post(
                        "http://localhost:8000/feedback",
                        json={
                            "query": st.session_state.messages[i - 1]["content"],
                            "answer": msg["content"],
                            "helpful": False,
                            "details": reason
                        }
                    )
                    st.warning("Thanks — we'll use your feedback to improve.")




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