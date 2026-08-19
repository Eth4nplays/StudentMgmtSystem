import streamlit as st
st.title("admin")
with st.sidebar:
    st.button("Logout", on_click=lambda: st.session_state.update({'logged_in': "None"}))