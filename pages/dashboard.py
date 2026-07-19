import streamlit as st

def show_dashboard():

    st.markdown("## 📊 Dashboard")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Reports Generated",
            len(st.session_state.history)
        )

    with c2:
        st.metric(
            "Current Session",
            len(st.session_state.history)
        )

    with c3:
        st.metric(
            "LLM",
            "Gemini 2.5 Flash"
        )

    st.divider()