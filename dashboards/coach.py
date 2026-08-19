import streamlit as st
st.title("coach")
with st.sidebar:
    st.button("Logout", on_click=lambda: st.query_params.update({'logged_in': "None"}))