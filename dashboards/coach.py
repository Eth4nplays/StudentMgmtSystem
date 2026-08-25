import streamlit as st
from helpers.cookies import *

st.title("coach")
with st.sidebar:
    if st.button("Logout", icon=":material/logout:", key="logout"):
            logout()
            st.rerun()