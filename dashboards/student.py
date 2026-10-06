
from io import StringIO

import pandas as pd
import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from helpers.imagebuttons import *
import calendar
from datetime import datetime
import helpers.mongodb

if 'class_view' not in st.session_state:
    st.session_state['class_view'] = False

if 'activity_view' not in st.session_state:
    st.session_state['activity_view'] = False

if 'editing_activity' not in st.session_state:
    st.session_state['editing_activity'] = False

if cookies.getCookies("token") is not None:
    userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

if cookies.getCookies("uid") is not None:
    uid = cookies.getCookies("uid")
else:
    uid = st.session_state['uid']

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
    if any(student.split()[0] == uid for student in class_data.get('students', [])):
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.subheader(class_name)
                if st.button("View Class", key=f"view_{i[0]}"):
                    viewClass(i[0])
                action = st.menu_button("", type="tertiary", icon=":material/more_vert:", options=["Leave Class"], key=f"menu{class_name}")
                
                if action == "Leave Class":
                    firebase.leaveClass(userToken, class_name, uid)
                    st.rerun()

def viewActivity(date):
    st.session_state.update({"activity_view": True})
    st.session_state.update({"activityDate": date})
    st.rerun()

@st.dialog("Edit Submission")
def editSubmission(date, submission):
    submission = st.text_area("Submission", placeholder="Enter your submission here...", value=submission)
    if st.button("Submit"):
        if submission:
            if firebase.submitTask(userToken, f"{uid} {st.session_state['profile']['name']}", st.session_state['selected_class'], date, submission):
                st.rerun()
            else:
                st.warning("Apologies, but it seems that the submission deadline has passed.")
        else:
            st.warning("Please enter your submission before submitting.")

@st.dialog("Undo Submission")
def undoSubmission(date, file, fileId=None):
    st.write("Are you sure you want to undo your submission? This action cannot be undone.")
    with st.container(horizontal=True):
        if st.button("Yes"):
            if file:
                helpers.mongodb.delete(fileId)
            if firebase.unsubmitTask(userToken, f"{uid} {st.session_state['profile']['name']}", st.session_state['selected_class'], date):
                st.rerun()
            else:
                st.warning("Apologies, but it seems that the submission deadline has passed.")
        if st.button("No", type="primary"):
            st.rerun()


def activityViewer(date):
    class_data = firebase.getClass(userToken, st.session_state['selected_class'])["tasks"][date]
    if st.button("Back", type="tertiary", icon=":material/arrow_back:"):
        st.session_state.update({"activity_view": False})
        st.rerun()
    with st.container(horizontal=True):
                    st.header(class_data["title"])
    st.write(f"Due on **{datetime.strptime(class_data['deadline'], '%y %m %d %H %M').strftime('%d %B %Y, %I:%M %p')}** • Maximum Grade: **{class_data['totalGrade']}**")
    with st.container(border=True):
        st.markdown(class_data["contents"])
    st.divider()
    submissions = class_data.get("submissions", {}).get(f"{uid} {st.session_state['profile']['name']}")
    st.subheader("Your Submission")
    if submissions == None:
        text, file = st.tabs(["Text Submission", "File Submission"])
        with text:
            submission = st.text_area("Submission", placeholder="Enter your submission here...")
            if st.button("Submit"):
                if submission:
                    if firebase.submitTask(userToken, f"{uid} {st.session_state['profile']['name']}", st.session_state['selected_class'], date, submission):
                        st.success("Submission successful!")
                        st.rerun()
                    else:
                        st.warning("Apologies, but it seems that the submission deadline has passed.")
                else:
                    st.warning("Please enter your submission before submitting.")
        with file:
            uploaded_file = st.file_uploader("Upload your submission file", type=["pdf", "docx", "pptx", "xlsx", "txt", "png", "jpg", "jpeg"], accept_multiple_files=False)
            if st.button("Submit File"):
                if uploaded_file:
                    file_id = helpers.mongodb.upload(uploaded_file, filename=uploaded_file.name, contentType=uploaded_file.type)
                    if firebase.submitTask(userToken, f"{uid} {st.session_state['profile']['name']}", st.session_state['selected_class'], date, f"fileUpload:{file_id}"):
                        st.success("File submission successful!")
                        st.rerun()
                    else:
                        st.warning("Apologies, but it seems that the submission deadline has passed.")
                else:
                    st.warning("Please upload a file before submitting.")
    else:
        with st.container(border=True):
            # if the submission is a file upload
            if submissions["submission"].startswith("fileUpload:"):
                file_id = submissions["submission"].split("fileUpload:")[1]
                with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center"):
                    st.write(f"**Grade:** {str(submissions.get("grade", "Not graded yet"))} / {str(class_data["totalGrade"])}")
                    st.button("Undo Submission", type="tertiary", key="undo_submission", on_click=undoSubmission, args=(date,True, file_id), icon=":material/undo:")
                file_data = helpers.mongodb.download(file_id)
                st.download_button(
                    label="Download your submission",
                    data=file_data["data"],
                    file_name=file_data["filename"],
                    mime=file_data["contentType"],
                    icon=":material/download:",
                    key="download_submission",
                    type="primary"
                )
            # if the submission is a text submission
            else:
                with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center"):
                    st.write(f"**Grade:** {str(submissions.get("grade", "Not graded yet"))} / {str(class_data["totalGrade"])}")
                    st.button("Edit Submission", type="tertiary", key="edit_submission", on_click=editSubmission, args=(date,submissions["submission"]), icon=":material/edit:")
                    st.button("Undo Submission", type="tertiary", key="undo_submission", on_click=undoSubmission, args=(date,False), icon=":material/undo:")
                        
                    st.markdown(submissions["submission"])
        st.markdown(f''':material/comment: **Coach comment:** {submissions.get("comment", "No comment yet")}''')

def classViewer():
    if st.button("Back", type="tertiary", icon=":material/arrow_back:"):
        st.session_state.update({"class_view": False})
        st.rerun()

    st.header(st.session_state['selected_class'])

    activities, reports, schedule, people = st.tabs(["Activities", "Reports", "Schedule", "People"], on_change="rerun")

    class_data = firebase.getClass(userToken, st.session_state['selected_class'])

    with activities:
            if activities.open :
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

    with reports:
        st.subheader("Attendance Report")

        name = st.session_state['profile']['name']

        with st.container(horizontal=True):
            month = st.selectbox(
                "Month",
                range(1, 13),
                format_func=lambda m: calendar.month_name[m],
                index= datetime.now().month-1
            )

            year = st.selectbox(
                "Year",
                range(2025, datetime.now().year+1),
                index= datetime.now().year-2025
            )

        with st.container(border=True):
            # Build row for the chosen month
            rows = []
            num_days = calendar.monthrange(year, month)[1]

            total_attendance = 0
            total_days = 0

            for day in range(1, num_days + 1):
                date_str = f"{day:02d}-{month:02d}-{year}"
                records = class_data["attendance"].get(date_str, {})

                if name not in records:
                    continue
                else:
                    total_days += 1

                attended = records.get(name, False)

                rows.append({
                    "Date": date_str,
                    "Attendance": attended
                })

                if attended:
                    total_attendance += 1

            # Convert to DataFrame
            df = pd.DataFrame(rows)

            # Display table
            st.dataframe(df, width="stretch", hide_index=True)

        with st.container(horizontal=True):
            with st.container(border=True):
                st.text("Class Attendance Rate")
                try:
                    st.subheader(f"{round((total_attendance/total_days)*100, 1)}%")
                except:
                    st.subheader(f"0%")
            with st.container(border=True):
                st.text("Total Attendance")
                st.subheader(f"{total_attendance}/{total_days}")
                    

    if people.open:
        with people:
            
            if class_data:
                st.subheader("Coach")
                with st.container(horizontal=True, vertical_alignment="center", border=True):
                    st.write(firebase.getData(class_data["classOwner"], userToken)["name"])
                st.subheader("Students")
                for i in class_data["students"]:
                    with st.container(horizontal=True, vertical_alignment="center", border=True):
                        st.write(i.split()[1])
            else:
                st.error("Failed to retrieve class members.")

if not st.session_state['class_view']:
    st.title(f"Welcome, {st.session_state['profile']['name']}")

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
    if st.session_state['activity_view']:
            activityViewer(st.session_state['activityDate'])
    else:
        classViewer()