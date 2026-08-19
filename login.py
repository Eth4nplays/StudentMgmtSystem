import streamlit as st
st.title("Welcome!", text_alignment="center")

selection = st.segmented_control(
    "Login as:",
    options=["Admin", "Coach", "Student"],
    selection_mode="single",
    required=True,
    default="Admin"
)

userInput = st.text_input("Username", type="default")
passwordInput = st.text_input("Password", type="password")


if st.button("Login", type="primary", icon=":material/login:"):
    if selection == "Admin":
        st.session_state['logged_in'] = "Admin"
        st.rerun()
    elif selection == "Coach":
        st.session_state['logged_in'] = "Coach"
        st.rerun()
    elif selection == "Student":
        st.session_state['logged_in'] = "Student"
        st.rerun()