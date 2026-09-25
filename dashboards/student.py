
from io import StringIO

import pandas as pd
import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from helpers.imagebuttons import *

if 'class_view' not in st.session_state:
    st.session_state['class_view'] = False

if cookies.getCookies("token") is not None:
    userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

if cookies.getCookies("uid") is not None:
    uid = cookies.getCookies("uid")
else:
    uid = st.session_state['uid']

profile = firebase.getData(uid, userToken)

@st.dialog("Join Class")
def joinClass():
    classCode = st.text_input("Enter Class Code")
    if st.button("Join Class"):
        if classCode:
            result = firebase.joinClass(userToken, classCode.upper(), uid)
            if result:
                st.success("Successfully joined the class!")
                st.rerun()
            else:
                st.error("Failed to join the class. Please check the code and try again.")
        else:
            st.warning("Please enter a class code.")


def viewClass(className):
    st.session_state.update({"selected_class": className})
    st.session_state.update({"class_view": True})
    st.rerun()

def classCard(i):
    class_name, class_data = i
    # Check if student is in the class
    if uid in class_data.get('students', {}):
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.subheader(class_name)
                if st.button("View Class", key=f"view_{i[0]}"):
                    viewClass(i[0])
                action = st.menu_button("", type="tertiary", icon=":material/more_vert:", options=["Leave Class"], key=f"menu{class_name}")
                
                if action == "Leave Class":
                    firebase.leaveClass(userToken, class_name, uid)
                    st.rerun()
            

def classViewer():
    if st.button("Back", type="tertiary", icon=":material/arrow_back:"):
        st.session_state.update({"class_view": False})
        st.rerun()

    st.header(st.session_state['selected_class'])

    activities, reports, schedule, people = st.tabs(["Activities", "Reports", "Schedule", "People"])

    class_data = firebase.getClass(userToken, st.session_state['selected_class'])
    
    with schedule:
        if class_data:
            df = pd.read_csv(
                StringIO(class_data["classSchedule"].replace("\\n", "\n")),
                header=None,
                names=["Day", "Start Time", "End Time", "Activity"],
                skipinitialspace=True
            )
    
            st.dataframe(df, hide_index=True, width="stretch",             
                            column_config={
                                "Day": st.column_config.TextColumn(
                                    "Day",
                                ),
                                "Start Time": st.column_config.TimeColumn(
                                    "Start Time",
                                    format="hh:mm A",
                                ),
                                "End Time": st.column_config.TimeColumn(
                                    "End Time",
                                    format="hh:mm A",
                                ),
                                "Activity": st.column_config.TextColumn("Activity")
                            }
                        )
        else:
            st.error("Failed to retrieve class schedule.")
    
    with people:
        
        if class_data:
            st.subheader("Coach")
            with st.container(horizontal=True, vertical_alignment="center", border=True):
                st.write(firebase.getData(class_data["classOwner"], userToken)["name"])
            st.subheader("Students")
            for i in class_data["students"]:
                with st.container(horizontal=True, vertical_alignment="center", border=True):
                    st.write(firebase.getData(i, userToken)["name"])
        else:
            st.error("Failed to retrieve class members.")

if not st.session_state['class_view']:
    st.title(f"Welcome, {profile['name']}")

    imageButtons("dashboards/student/inbox.py", "assets/inbox.png", 1646, 316)

    with st.container(horizontal=True, vertical_alignment="bottom"):
        st.subheader("Your Classes", width="content")
        st.divider()
    
    list_of_classes = firebase.getClasses(userToken)
    for i in list_of_classes.items():
        classCard(i)

    if st.button("Join Class", width="stretch", icon=":material/add:", type="primary"):
        joinClass()

else:
    classViewer()