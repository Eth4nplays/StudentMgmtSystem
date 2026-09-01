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

    
def classCard():
    list_of_classes = firebase.getClasses(userToken)
    for i in list_of_classes.items():
        with st.container(border=True):
            with st.container(horizontal=True):
                st.subheader(i[0], width="stretch")
                st.caption(f"Code: {i[1]['code']}")
            st.write(i[1]['classSchedule'])
            st.button("View Class", key=f"view_{i[0]}", on_click=lambda class_name=i[0]: st.session_state.update({"selected_class": class_name}))
            st.button("Delete Class", key=f"delete_{i[0]}", on_click=lambda class_name=i[0]: firebase.deleteClass(userToken, class_name))
classCard()