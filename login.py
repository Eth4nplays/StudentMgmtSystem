import streamlit as st
import firebase
st.title("Welcome!", text_alignment="center")

emailInput = st.text_input("Email", type="default")
passwordInput = st.text_input("Password", type="password")

if st.button("Login", type="primary", icon=":material/login:"):
    result = firebase.login(emailInput, passwordInput)
    if result:
        st.query_params["uid"] = result["localId"]
        st.query_params["id_token"] = result["idToken"]
        st.query_params["refresh_token"] = result["refreshToken"]

        profile = firebase.getRole(
            result["localId"],
            result["idToken"]
        )

        st.query_params["role"] = profile["role"]

        st.rerun()
    else:
        st.error("Invalid email or password.")

