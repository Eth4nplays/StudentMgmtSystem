import datetime
from io import StringIO
import string

import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from helpers.imagebuttons import *
import random
import pandas as pd
from datetime import time
import helpers.mongodb

if 'class_view' not in st.session_state:
    st.session_state['class_view'] = False

if 'activity_view' not in st.session_state:
    st.session_state['activity_view'] = False

if 'editing_activity' not in st.session_state:
    st.session_state['editing_activity'] = False

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

def viewActivity(date):
    st.session_state.update({"activity_view": True})
    st.session_state.update({"activityDate": date})
    st.rerun()

def classCard(i):
    # check if the coach actually owns the class
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(i[0], width="content")

        if st.button("View Activities", key=f"view_{i[0]}"):
            viewClass(i[0])


@st.dialog("Submission")
def viewSubmission(class_data, student_name, submission, date):
    with st.container(border=True):
        if submission.startswith("fileUpload:"):
            file_id = submission.split("fileUpload:")[1]
            file_data = helpers.mongodb.download(file_id)
            st.markdown(f":material/attachment: {file_data['filename']}")
            st.download_button(
                label="Download Submission",
                data=file_data["data"],
                file_name=file_data["filename"],
                mime=file_data["contentType"],
                key="download_submission",
                icon=":material/download:",
                type="primary"
            )
        else:
            st.markdown(submission)

    try:
        currentGrade = class_data["submissions"][student_name].get("grade", 0)
    except:
        currentGrade = 0
    with st.container(border=True):
        st.write(":material/grade: Grade: " + str(currentGrade) +" / " + str(class_data["totalGrade"]))
        st.write(":material/comment: Coach Comment:")
        st.markdown(class_data["submissions"][student_name].get("comment", "No comment yet."))

def activityViewer(date):
    class_data = firebase.getClass(userToken, st.session_state['selected_class'])["tasks"][date]
    if not st.session_state['editing_activity']:
        if st.button("Back", type="tertiary", icon=":material/arrow_back:"):
            st.session_state.update({"activity_view": False})
            st.rerun()
        with st.container(horizontal=True):
                        st.header(class_data["title"])
                        if st.button("Edit Activity", type="tertiary", icon=":material/edit:"):
                            st.session_state['editing_activity'] = True
                            st.rerun()
        st.write(f"Due on **{datetime.datetime.strptime(class_data['deadline'], '%y %m %d %H %M').strftime('%d %B %Y, %I:%M %p')}** • Maximum Grade: **{class_data['totalGrade']}**")
        with st.container(border=True):
            st.markdown(class_data["contents"])
        st.divider()
        st.subheader("Submissions")
        try:
            for i in class_data["submissions"]:
                student_name = i.split()[1]
                with st.container(horizontal=True, vertical_alignment="center", border=True):
                    st.write(student_name)
                    with st.container(horizontal=True, horizontal_alignment="right"):
                        try:
                            st.write(f"{class_data['submissions'][i]['grade']}/{class_data['totalGrade']}")
                        except:
                            st.write(f"Ungraded")
                    if st.button("View Submission", key=f"view_{student_name}"):
                        viewSubmission(class_data, i, class_data['submissions'][i]['submission'], date)
        except Exception as e:
            st.write(f"No submissions yet. {e}")
        
    else:
        
        with st.container(horizontal=True):
            title= st.text_input("Activity Title", value=class_data["title"], key="edit_title")
        with st.container(horizontal=True):
            deadline_date = st.date_input("Deadline", format="DD/MM/YYYY", value=datetime.datetime.strptime(class_data['deadline'], '%y %m %d %H %M').date(), key="edit_deadline_date")
            deadline_time = st.time_input("Time", value=datetime.datetime.strptime(class_data['deadline'], '%y %m %d %H %M').time(), key="edit_deadline_time")
        max_total_grade = st.number_input("Max Total Grade", min_value=0, step=1, value=class_data["totalGrade"])
        content = st.text_area("Activity Contents", value=class_data["contents"], key="edit_contents")

        if st.button("Save and Exit", type="primary", icon=":material/arrow_back:"):
            st.session_state.update({"editing_activity": False})
            firebase.editTask(userToken , className=st.session_state['selected_class'], date=date, taskName=title, contents=content, totalGrade=max_total_grade, deadline=(deadline_date.strftime("%y %m %d") + " " + deadline_time.strftime("%H %M")))

            st.rerun()

def classViewer():

    if st.button("Back", type="tertiary", icon=":material/arrow_back:"):
        st.session_state.update({"class_view": False})
        st.rerun()

    st.header(st.session_state['selected_class'])
    class_data = firebase.getClass(userToken, st.session_state['selected_class'])

    try:
        for i in class_data["tasks"]:
            with st.container(horizontal=True, vertical_alignment="center", border=True):
                with st.container():
                    st.write(class_data["tasks"][i]["title"])
                    if st.button("View Activity", key=f"view_{class_data['tasks'][i]}"):
                        viewActivity(i)
    except Exception as e:
        st.write(e)
        st.write("No activities found. Create your first one below!")

if not st.session_state['class_view']:
    st.page_link("dashboards/admin.py", label="Back", icon=":material/arrow_back:")

    st.title(f"Activities")
            
    list_of_classes = firebase.getClasses(userToken)
    for i in list_of_classes.items():
        classCard(i)


else:
    if st.session_state['activity_view']:
        activityViewer(st.session_state['activityDate'])
    else:
        classViewer()