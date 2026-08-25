import streamlit as st
import extra_streamlit_components as stx
import helpers.firebase as firebase
from helpers.cookies import *
st.title("Welcome!", text_alignment="center")

emailInput = st.text_input("Email", type="default", key="emailLogin")
passwordInput = st.text_input("Password", type="password", key="pwLogin")

if st.button("Login", type="primary", icon=":material/login:", key="loginButton"):
    result = firebase.login(emailInput, passwordInput)
    if result:
        batchCookies({"uid":result["localId"],
                      "token":result["idToken"],
                      "refreshToken":result["refreshToken"]})
        st.session_state['uid'] = result["localId"]
        st.session_state['token'] = result["idToken"]
        
    else:
        st.error("Invalid email or password.")

