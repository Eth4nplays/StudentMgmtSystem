
import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from helpers.imagebuttons import *

if cookies.getCookies("token") is not None:
    userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

if cookies.getCookies("uid") is not None:
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
                st.rerun()
            else:
                st.error("Failed to join the class. Please check the code and try again.")
        else:
            st.warning("Please enter a class code.")

if st.button("Join Class"):
    joinClass()



def classCard(i):
    class_name, class_data = i
    # Check if student is in the class
    if uid in class_data.get('students', {}):
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.subheader(class_name, width="content")
                st.caption(f"Code: {class_data['code']}")
                action = st.menu_button("", type="tertiary", icon=":material/more_vert:", options=["Leave Class"], key=f"menu{class_name}")
                
                if action == "Leave Class":
                    firebase.leaveClass(userToken, class_name, uid)
                    st.rerun()
            st.write(class_data['classSchedule'])
            st.button("View Class", key=f"view_{class_name}", on_click=lambda class_name=class_name: st.session_state.update({"selected_class": class_name}))

list_of_classes = firebase.getClasses(userToken)
for i in list_of_classes.items():
    classCard(i)

    