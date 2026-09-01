import string

import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from helpers.imagebuttons import *
import random

if 'class_view' not in st.session_state:
    st.session_state['class_view'] = False

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

if cookies.getCookies("uid") != None:
        uid = cookies.getCookies("uid")
else:
    uid = st.session_state['uid']

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

@st.dialog("Delete Class?")
def deleteClass(className):
    st.write(f"Are you sure you want to delete {className}?")
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button("Yes"):
            firebase.deleteClass(userToken, className)
            st.rerun()
        elif st.button("No", type="primary"):
            st.rerun()

def viewClass(className):
    st.session_state.update({"selected_class": className})
    st.session_state.update({"class_view": True})
    st.rerun()

def classCard(i):
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(i[0], width="content")
            st.caption(f"Code: {i[1]['code']}")
            action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=["Delete Class"], key=f"menu{i[0]}")

            if action == "Delete Class":
                deleteClass(i[0])
        if st.button("View Class", key=f"view_{i[0]}"):
            viewClass(i[0])



if not st.session_state['class_view']:

    st.title("Welcome, Coach")

    imageButtons("dashboards/coach/inbox.py", "assets/inbox.png", 1646, 316)

    st.subheader("Your Classes")
                
    if st.button("Create Class"):
        createClass()

            
    list_of_classes = firebase.getClasses(userToken)
    for i in list_of_classes.items():
        classCard(i)

else:
    if st.button("Back", type="tertiary", icon=":material/arrow_back:"):
        st.session_state.update({"class_view": False})
        st.rerun()

    st.header(st.session_state['selected_class'])

    activities, attendance, reports, schedule, people = st.tabs(["Activities", "Attendance", "Reports", "Schedule", "People"])

    with schedule:
        
        st.subheader("Class Schedule")
        class_data = firebase.getClass(userToken, st.session_state['selected_class'])
        if class_data:
            st.write(class_data["classSchedule"])
        else:
            st.error("Failed to retrieve class schedule.")
