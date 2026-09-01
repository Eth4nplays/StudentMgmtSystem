import string

import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from helpers.imagebuttons import *
import random

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

if cookies.getCookies("uid") != None:
        uid = cookies.getCookies("uid")
else:
    uid = st.session_state['uid']

st.title("Welcome, Coach")

imageButtons("dashboards/coach/inbox.py", "assets/inbox.png", 1646, 316)

st.subheader("Your Classes")

@st.dialog("Create Class")
def createClass():
    className = st.text_input("Class Name")
    
    classSchedule = st.text_area("Class Schedule")
    if st.button("Create Class"):
        if className and classSchedule:
            result = firebase.createClass(
                userToken,
                classSchedule,
                ''.join(random.choices(string.ascii_letters + string.digits, k=6)).upper(),
                className,
                uid
            )
            if result:
                st.success(f"Class '{className}' created successfully!")
                class_data = firebase.getClass(userToken, className)
                st.write("Class Code:")
                if class_data:
                    st.code(class_data["code"], width="content")
            else:
                st.error("Failed to create class. Please try again.")
        else:
            st.warning("Please fill in all fields.")

if st.button("Create Class"):
    createClass()