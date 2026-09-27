from io import StringIO
import string

import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from helpers.imagebuttons import *
import random
import pandas as pd
from datetime import time

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

    df = pd.read_csv(
            StringIO(""),
            header=None,
            names=["Day", "Start Time", "End Time", "Activity"],
            skipinitialspace=True
        )
    
    for i in ["Start Time", "End Time"]:
        df[i] = pd.to_datetime(df[i], format="%H:%M:%S").dt.time

    classSchedule = st.data_editor(
            df,
            hide_index=True,
            width="stretch",
            num_rows="dynamic",
            column_config={
                "Day": st.column_config.SelectboxColumn(
                    "Day",
                    options=[
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday"
                    ],
                    required=True
                ),
                "Start Time": st.column_config.TimeColumn(
                    "Start Time",
                    format="hh:mm A",
                    required=True
                ),
                "End Time": st.column_config.TimeColumn(
                    "End Time",
                    format="hh:mm A",
                    required=True
                ),
                "Activity": st.column_config.TextColumn("Activity")
            }
        )
    
    if st.button("Create Class"):
        Schedule = classSchedule.to_csv(
                        index=False,
                        header=False
                    ).strip()
        if className and Schedule:
            
            result = firebase.createClass(
                userToken,
                Schedule,
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

                st.rerun()
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
    # check if the coach actually owns the class
    if uid in i[1].get('classOwner'):
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.subheader(i[0], width="content")
                st.caption(f"Code: {i[1]['code']}")
                action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=["Delete Class"], key=f"menu{i[0]}")

                if action == "Delete Class":
                    deleteClass(i[0])
            if st.button("View Class", key=f"view_{i[0]}"):
                viewClass(i[0])

@st.dialog("Edit Schedule")
def editSchedule(class_data):
    # shows a table to edits the class schedule using and saves to firebase

    
    df = pd.read_csv(
        StringIO(class_data["classSchedule"].replace("\\n", "\n")),
        header=None,
        names=["Day", "Start Time", "End Time", "Activity"],
        skipinitialspace=True
    )

    for i in ["Start Time", "End Time"]:
        df[i] = pd.to_datetime(df[i], format="%H:%M:%S").dt.time

    edited = st.data_editor(
        df,
        hide_index=True,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "Day": st.column_config.SelectboxColumn(
                "Day",
                options=[
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday"
                ],
                required=True
            ),
            "Start Time": st.column_config.TimeColumn(
                "Start Time",
                format="hh:mm A",
                required=True
            ),
            "End Time": st.column_config.TimeColumn(
                "End Time",
                format="hh:mm A",
                required=True
            ),
            "Activity": st.column_config.TextColumn("Activity")
        }
    )

    if st.button("Submit"):
        newSchedule = edited.to_csv(
            index=False,
            header=False
        ).strip()
        
        result = firebase.editClass(
            userToken,
            st.session_state["selected_class"],
            "classSchedule",
            newSchedule
        )
        if result:
            st.success("Schedule updated successfully!")
            st.rerun()
        else:
            st.error("Failed to update schedule.")



def classViewer():

    if st.button("Back", type="tertiary", icon=":material/arrow_back:"):
        st.session_state.update({"class_view": False})
        st.rerun()

    st.header(st.session_state['selected_class'])

    activities, attendance, reports, schedule, people = st.tabs(["Activities", "Attendance", "Reports", "Schedule", "People"], on_change="rerun")
    class_data = firebase.getClass(userToken, st.session_state['selected_class'])

    with attendance:
        date = st.date_input("Select Date", value=None, min_value=None, max_value=None, key="attendance_date", format="DD-MM-YYYY")
        if date:
            try:
                # if attendance data is available / if date is selected
                with st.form("attendance_form", border=False):
                    edited_df = st.data_editor(pd.DataFrame(
                        class_data["attendance"][date.strftime("%d-%m-%Y")].items(),
                        columns=["Student", "Attendance"]), hide_index=True, width="stretch", key=f"attendance_editor_{date.strftime("%d-%m-%Y")}")
                    if st.form_submit_button("Submit"):
                        payload = edited_df.set_index("Student").to_dict()["Attendance"]
                        print(firebase.editAttendance(id_token=userToken, 
                                                className=st.session_state['selected_class'], 
                                                field=date.strftime("%d-%m-%Y"), 
                                                value=payload))
                        st.success("Attendance updated successfully!")
            except:
                try:
                    # if date is selected, however attendance data is not available
                    # initialize new attendance data with payload
                    payload = {}
                    for i in class_data["students"]:
                        payload[i.split()[1]] = False
                    firebase.editAttendance(id_token=userToken, 
                                            className=st.session_state['selected_class'], 
                                            field=date.strftime("%d-%m-%Y"), 
                                            value=payload)
                    st.rerun()
                except Exception as e:
                    st.error(f"An error has occured.{e}")
            
    with schedule:
        with st.container(horizontal=True, vertical_alignment="center"):
            if st.button("Edit", type="secondary", icon=":material/edit:"):
                editSchedule(class_data)
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
                st.write(st.session_state['profile']['name'])
            st.subheader("Students")
            try:
                for i in class_data["students"]:
                    with st.container(horizontal=True, vertical_alignment="center", border=True):
                        st.write(i.split()[1])
                        action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=["Remove Student"], key=f"menu{i[0]}")
                        if action == "Remove Student":
                            firebase.leaveClass(userToken, st.session_state['selected_class'], i)
            except:
                st.write("No students found")
        else:
            st.error("Failed to retrieve class members.")

    with reports:
        # show a graph depicting class attendance
        st.subheader("Class Attendance Report")
        #show graph taking data from attendance

        attendance_report_dict = {}
        individual_attendance = {}
        max_attendance = 0
        total_attendance = 0
        totaldaysofattendance = len(class_data["attendance"])

        try:
            for i in (class_data["students"]):
                for j in (class_data["attendance"]):
                    if i.split()[1] in class_data["attendance"][j]:
                        individual_attendance[i.split()[1]] = individual_attendance.get(i.split()[1], 0) + (1 if class_data["attendance"][j][i.split()[1]] == True else 0)
            for i in (class_data["attendance"]):
                count = 0
                for j in class_data["attendance"][i]:
                    if class_data["attendance"][i][j] == True:
                        count += 1
                        total_attendance += 1
                    max_attendance += 1
                attendance_report_dict[i] = count
            st.write(individual_attendance)

            df = pd.DataFrame(list(attendance_report_dict.items()), columns=["Date", "Number of Students"])

            with st.container(border=True):
                st.bar_chart(df, x="Date", y="Number of Students", color="Number of Students")
            with st.container(border=True):
                st.text("Class Attendance Rate")
                st.subheader(f"{(total_attendance/max_attendance)*100}%")
            with st.container(border=True):
                st.text("Individual Student Attendance")
                st.dataframe(pd.DataFrame(list(individual_attendance.items()), columns=["Student", "Number of Classes Attended"]))

        except:
            st.write("No attendance data yet.")

        st.subheader("Class Academic Report")




if not st.session_state['class_view']:
    st.title(f"Welcome, {st.session_state['profile']['name']}")

    imageButtons("dashboards/coach/inbox.py", "assets/inbox.png", 1646, 316)
    with st.container(horizontal=True, vertical_alignment="bottom"):
        st.subheader("Your Classes", width="content")
        st.divider()
    

            
    list_of_classes = firebase.getClasses(userToken)
    for i in list_of_classes.items():
        classCard(i)

    if st.button("Create Class", width="stretch", icon=":material/add:", type="primary"):
        createClass()

else:
    classViewer()