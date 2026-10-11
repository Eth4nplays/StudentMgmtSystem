import streamlit as st
import extra_streamlit_components as stx
import helpers.firebase as firebase
from helpers.cookies import *
from helpers.information import *
st.title("Welcome!", text_alignment="center")
infobox('''Please contact your admin for your login credentials.

If you are an admin, please create an account from the **"Manage Accounts"** page.''', text="Information", icon=":material/info:")
with st.form("login_form"):

    emailInput = st.text_input("Email", type="default", key="emailLogin")
    passwordInput = st.text_input("Password", type="password", key="pwLogin")
    
    login = st.form_submit_button("Login", type="primary", icon=":material/login:", key="loginButton")

    if login:
        result = firebase.login(emailInput.strip(), passwordInput.strip())
        if result:
            batchCookies({"uid":result["localId"],
                        "token":result["idToken"],
                        "refreshToken":result["refreshToken"]})
            st.session_state['uid'] = result["localId"]
            st.session_state['token'] = result["idToken"]
            st.rerun()
        else:
            st.error("Invalid email or password.")