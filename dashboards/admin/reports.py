import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from helpers.imagebuttons import *
import pandas as pd

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

def viewClass(className):
    st.session_state.update({"selected_class": className})
    st.session_state.update({"class_view": True})
    st.rerun()



def classCard(i):
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(i[0], width="content")
            
        if st.button("View Report", key=f"view_{i[0]}"):
            viewClass(i[0])

def classViewer():

    if st.button("Back", type="tertiary", icon=":material/arrow_back:"):
        st.session_state.update({"class_view": False})
        st.rerun()

    st.header(st.session_state['selected_class'])

    class_data = firebase.getClass(userToken, st.session_state['selected_class'])

    attendance, academic = st.tabs([":material/assignment: Attendance", ":material/school: Academic"])

    with attendance:
        #show graph taking data from attendance
        attendance_report_dict = {}
        individual_attendance = {}
        max_attendance = 0
        total_attendance = 0

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
    with academic:
        st.write("nyanya :3")




if not st.session_state['class_view']:
    st.title(f"Reports")
    list_of_classes = firebase.getClasses(userToken)
    for i in list_of_classes.items():
        classCard(i)
else:
    classViewer()