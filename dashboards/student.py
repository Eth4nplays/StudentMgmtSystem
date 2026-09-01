
import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from helpers.imagebuttons import *
st.title("student")

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

if cookies.getCookies("uid") != None:
        uid = cookies.getCookies("uid")
else:
    uid = st.session_state['uid']

st.title("Welcome, Student")

imageButtons("dashboards/student/inbox.py", "assets/inbox.png", 1646, 316)

st.subheader("Your Classes")

@st.dialog("Join Class")
def joinClass():
    classCode = st.text_input("Enter Class Code")
    if st.button("Join Class"):
        if classCode:
            result = firebase.joinClass(userToken, classCode, uid)
            if result:
                st.success("Successfully joined the class!")
            else:
                st.error("Failed to join the class. Please check the code and try again.")
        else:
            st.warning("Please enter a class code.")

if st.button("Join Class"):
    joinClass()

def classCard():
    list_of_classes = firebase.getClasses(userToken)
    for i in list_of_classes.items():
        with st.container(border=True):
            with st.container(horizontal=True):
                st.subheader(i[0], width="stretch")
                st.caption(f"Code: {i[1]['code']}")
            st.write(i[1]['classSchedule'])
            st.button("View Class", key=f"view_{i[0]}", on_click=lambda class_name=i[0]: st.session_state.update({"selected_class": class_name}))
            st.button("Leave Class", key=f"leave_{i[0]}", on_click=lambda class_name=i[0]: firebase.leaveClass(userToken, class_name, uid))
classCard()

    