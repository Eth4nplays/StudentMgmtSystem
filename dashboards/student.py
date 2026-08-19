import streamlit as st
st.title("student")
with st.sidebar:
    if st.button("Logout", icon=":material/logout:"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()