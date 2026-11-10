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
from helpers.localization import localized_month_name, normalize_language, translate

language = normalize_language(st.session_state["profile"].get("language"))
tr = lambda text: translate(text, language)

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

        if st.button(tr("View Activities"), key=f"view_{i[0]}"):
            viewClass(i[0])


@st.dialog(tr("Submission"))
def viewSubmission(class_data, student_name, submission, date):
    with st.container(border=True):
        if submission.startswith("fileUpload:"):
            file_id = submission.split("fileUpload:")[1]
            with st.spinner(tr("Loading submission...")):
                file_data = helpers.mongodb.download(file_id)
            st.markdown(f":material/attachment: {file_data['filename']}")
            st.download_button(
                label=tr("Download Submission"),
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
        currentGrade = "Ungraded"
    with st.container(border=True):
        st.write(f":material/grade: {tr('Grade:')} {currentGrade} / {class_data['totalGrade']}")
        st.write(f":material/comment: {tr('Coach Comment:')}")
        st.markdown(class_data["submissions"][student_name].get("comment", tr("No comment yet.")))

def activityViewer(date):
    class_data = firebase.getClass(userToken, st.session_state['selected_class'])["tasks"][date]
    if not st.session_state['editing_activity']:
        if st.button(tr("Back"), type="tertiary", icon=":material/arrow_back:"):
            st.session_state.update({"activity_view": False})
            st.rerun()
        with st.container(horizontal=True):
                        st.header(class_data["title"])
                        if st.button(tr("Edit Activity"), type="tertiary", icon=":material/edit:"):
                            st.session_state['editing_activity'] = True
                            st.rerun()
        deadline = datetime.datetime.strptime(class_data["deadline"], "%y %m %d %H %M")
        st.write(f"{tr('Due on')} **{deadline.day:02d} {localized_month_name(deadline.month, language)} {deadline.year}, {deadline.strftime('%I:%M %p')}** • {tr('Maximum Grade')}: **{class_data['totalGrade']}**")
        with st.container(border=True):
            st.markdown(class_data["contents"])
        st.divider()
        st.subheader(tr("Submissions"))
        try:
            for i in class_data["submissions"]:
                student_name = i.split()[1]
                with st.container(horizontal=True, vertical_alignment="center", border=True):
                    st.write(student_name)
                    with st.container(horizontal=True, horizontal_alignment="right"):
                        try:
                            st.write(f"{class_data['submissions'][i]['grade']}/{class_data['totalGrade']}")
                        except:
                            st.write(tr("Ungraded"))
                    if st.button(tr("View Submission"), key=f"view_{student_name}"):
                        viewSubmission(class_data, i, class_data['submissions'][i]['submission'], date)
        except Exception as e:
            st.write(tr("No submissions yet."))
        
    else:
        
        with st.container(horizontal=True):
            title= st.text_input(tr("Activity Title"), value=class_data["title"], key="edit_title")
        with st.container(horizontal=True):
            deadline_date = st.date_input(tr("Deadline"), format="DD/MM/YYYY", value=datetime.datetime.strptime(class_data['deadline'], '%y %m %d %H %M').date(), key="edit_deadline_date")
            deadline_time = st.time_input(tr("Time"), value=datetime.datetime.strptime(class_data['deadline'], '%y %m %d %H %M').time(), key="edit_deadline_time")
        max_total_grade = st.number_input(tr("Max Total Grade"), min_value=0, step=1, value=class_data["totalGrade"])
        content = st.text_area(tr("Activity Contents"), value=class_data["contents"], key="edit_contents")

        if st.button(tr("Save and Exit"), type="primary", icon=":material/arrow_back:"):
            st.session_state.update({"editing_activity": False})
            firebase.editTask(userToken , className=st.session_state['selected_class'], date=date, taskName=title, contents=content, totalGrade=max_total_grade, deadline=(deadline_date.strftime("%y %m %d") + " " + deadline_time.strftime("%H %M")))

            st.rerun()

def classViewer():

    if st.button(tr("Back"), type="tertiary", icon=":material/arrow_back:"):
        st.session_state.update({"class_view": False})
        st.rerun()

    st.header(st.session_state['selected_class'])
    class_data = firebase.getClass(userToken, st.session_state['selected_class'])

    try:
        for i in class_data["tasks"]:
            with st.container(horizontal=True, vertical_alignment="center", border=True):
                with st.container():
                    st.write(class_data["tasks"][i]["title"])
                    if st.button(tr("View Activity"), key=f"view_{class_data['tasks'][i]}"):
                        viewActivity(i)
    except Exception as e:
        st.write(f"{tr('No activities found.')} {e}")

if not st.session_state['class_view']:
    st.page_link("dashboards/admin.py", label=tr("Back"), icon=":material/arrow_back:")

    st.title(tr("Activities"))
            
    list_of_classes = firebase.getClasses(userToken)
    for i in list_of_classes.items():
        classCard(i)


else:
    if st.session_state['activity_view']:
        activityViewer(st.session_state['activityDate'])
    else:
        classViewer()