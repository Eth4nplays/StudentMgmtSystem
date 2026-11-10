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
from helpers.localization import (
    localized_asset_path,
    localized_month_name,
    normalize_language,
    translate,
)

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

def hasUnreadAnnouncement():
    announcements = firebase.getAnnouncement(userToken)
    if not announcements:
        return False

    available_roles = {"Coach", st.session_state['profile']['name']}
    available_dates = [
        datetime.datetime.strptime(date, "%y %m %d %H %M")
        for date, announcement in announcements.items()
        if available_roles.intersection(announcement.get("roles", []))
    ]
    if not available_dates:
        return False

    latest_announcement = max(available_dates)
    last_read = (
        st.session_state['profile'].get("lastreadannouncement")
        or st.session_state['profile'].get("lastread")
    )
    if not last_read:
        return True

    last_read_announcement = datetime.datetime.strptime(last_read, "%y %m %d %H %M")
    return latest_announcement > last_read_announcement

if "has_unread_announcement" not in st.session_state:
    st.session_state["has_unread_announcement"] = hasUnreadAnnouncement()

@st.dialog(tr("Create Class"))
def createClass():
    className = st.text_input(tr("Class Name"))

    df = pd.read_csv(
            StringIO(""),
            header=None,
            names=["Day", "Start Time", "End Time", "Activity"],
            skipinitialspace=True
        )
    
    for i in ["Start Time", "End Time"]:
        df[i] = pd.to_datetime(df[i], format="%H:%M:%S").dt.time

    st.write(tr("Class schedule"))
    classSchedule = st.data_editor(
            df,
            hide_index=True,
            width="stretch",
            num_rows="dynamic",
            column_config={
                "Day": st.column_config.SelectboxColumn(
                    tr("Day"),
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
                    tr("Start Time"),
                    format="hh:mm A",
                    required=True
                ),
                "End Time": st.column_config.TimeColumn(
                    tr("End Time"),
                    format="hh:mm A",
                    required=True
                ),
                "Activity": st.column_config.TextColumn(tr("Activity"))
            }
        )
    
    if st.button(tr("Create Class")):
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
                st.success(f"{tr('Class')} '{className}' {tr('created successfully!')}")
                class_data = firebase.getClass(userToken, className)
                st.write(tr("Class Code:"))
                if class_data:
                    st.code(class_data["code"], width="content")

                st.rerun()
            else:
                st.error(tr("Failed to create class. Please try again."))
        else:
            st.warning(tr("Please fill in all fields."))

@st.dialog(tr("Delete Class?"))
def deleteClass(className):
    st.write(f"{tr('Are you sure you want to delete')} {className}?")
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button(tr("Yes")):
            firebase.deleteClass(userToken, className)
            st.rerun()
        elif st.button(tr("No"), type="primary"):
            st.rerun()

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
    if uid in i[1].get('classOwner'):
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.subheader(i[0], width="content")
                st.caption(f"{tr('Code')}: {i[1]['code']}")
                action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=[tr("Delete Class")], key=f"menu{i[0]}")

                if action == tr("Delete Class"):
                    deleteClass(i[0])
            if st.button(tr("View Class"), key=f"view_{i[0]}"):
                viewClass(i[0])

@st.dialog(tr("Edit Schedule"))
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
            tr("Day"),
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
            tr("Start Time"),
                format="hh:mm A",
                required=True
            ),
            "End Time": st.column_config.TimeColumn(
            tr("End Time"),
                format="hh:mm A",
                required=True
            ),
            "Activity": st.column_config.TextColumn(tr("Activity"))
        }
    )

    if st.button(tr("Submit")):
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
            st.success(tr("Schedule updated successfully!"))
            st.rerun()
        else:
            st.error(tr("Failed to update schedule."))

@st.dialog(tr("Create Activity"))
def addActivity(class_data):
    id_token = userToken
    className = st.session_state['selected_class']
    activity_name = st.text_input(tr("Activity Name"))
    content = st.text_area(tr("Activity Description"))
    max_total_grade = st.number_input(tr("Max Total Grade"), min_value=0, step=1, value=100)
    with st.container(horizontal=True):
        deadline_date = st.date_input(tr("Deadline"), format="DD/MM/YYYY")
        deadline_time = st.time_input(tr("Time"))

    
    if st.button(tr("Add")):
        firebase.createTask(id_token , className, activity_name, content, max_total_grade, (deadline_date.strftime("%y %m %d") + " " + deadline_time.strftime("%H %M")))
        st.rerun()

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
    st.divider()
    try:
        currentGrade = class_data["submissions"][student_name].get("grade", 0)
    except:
        currentGrade = 0
    with st.container(horizontal=True, vertical_alignment="bottom"):
        grade = st.number_input(tr("Grade"), min_value=0, max_value=class_data["totalGrade"], step=1, value=currentGrade)
        st.write("/ " + str(class_data["totalGrade"]))
    comment = st.text_area(tr("Comment"), value=class_data["submissions"][student_name].get("comment", ""))
    if st.button(tr("Submit")):
        firebase.gradeTask(userToken, student_name, st.session_state['selected_class'], st.session_state['activityDate'], grade, comment)
        firebase.setAnnouncement(userToken, title=f"Graded: {class_data['title']}", content=f'''Your submission for {class_data['title']} has been graded. You received a grade of {grade}/{class_data['totalGrade']}.
                                 
**:material/comment: Comment:** {comment}''', roles=[student_name.split()[1]], date=datetime.datetime.now().strftime("%y %m %d %H %M"))
        
        st.rerun()


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

@st.dialog(tr("Delete Activity?"))
def deleteActivity(class_data, i):
    st.write(f"{tr('Are you sure you want to delete')} {class_data['tasks'][i]['title']}?")
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button(tr("Yes")):
            firebase.deleteTask(userToken, st.session_state['selected_class'], i)
            st.rerun()
        if st.button(tr("No"), type="primary"):
            st.rerun()

def classViewer():

    if st.button(tr("Back"), type="tertiary", icon=":material/arrow_back:"):
        st.session_state.update({"class_view": False})
        st.rerun()

    st.header(st.session_state['selected_class'])

    activities, attendance, reports, schedule, people = st.tabs([tr("Activities"), tr("Attendance"), tr("Reports"), tr("Schedule"), tr("People")], on_change="rerun")
    with st.spinner("Loading class data..."):
        class_data = firebase.getClass(userToken, st.session_state['selected_class'])

    
    with activities:
        if activities.open :
            with st.bottom:
                st.button(tr("Add Activity"), type="primary", icon=":material/add:", on_click=addActivity, args=(class_data,))
            try:
                for i in class_data["tasks"]:
                    with st.container(horizontal=True, vertical_alignment="center", border=True):
                        with st.container():
                            st.write(class_data["tasks"][i]["title"])
                            if st.button(tr("View Activity"), key=f"view_{class_data['tasks'][i]}"):
                                viewActivity(i)
                        action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=[tr("Delete Activity")], key=f"menu{class_data['tasks'][i]}")
                        if action == tr("Delete Activity"):
                            deleteActivity(class_data, i)
            except Exception as e:
                st.write(tr("No activities found. Create your first one below!"))
                    



    with attendance:
        if st.button(tr("Scan Attendance"), type="primary", icon=":material/qr_code:"):
            st.switch_page("dashboards/coach/attendancescan.py")
        date = st.date_input(
            tr("Select Date"),
            value=datetime.date.today(),
            min_value=None,
            max_value=datetime.date.today(),
            key="attendance_date",
            format="DD-MM-YYYY"
        )

        if date:
            date_str = date.strftime("%d-%m-%Y")

            try:
                attendance_data = class_data["attendance"][date_str]

            except KeyError:
                # Initialize attendance if the selected date does not exist
                attendance_data = {}

                for i in class_data["students"]:
                    attendance_data[i.split()[1]] = {
                        "0": False,
                        "1": ""
                    }

                firebase.editAttendance(
                    id_token=userToken,
                    className=st.session_state["selected_class"],
                    field=date_str,
                    value=attendance_data
                )

                st.rerun()

            # Convert different formats into a consistent dataframe
            rows = []

            for student, value in attendance_data.items():
                if isinstance(value, dict):
                    status = value.get("0", False)
                    remarks = value.get("1", "")

                elif isinstance(value, (list, tuple)):
                    status = value[0] if len(value) > 0 else False
                    remarks = value[1] if len(value) > 1 else ""

                else:
                    status = value
                    remarks = ""

                rows.append({
                    "Student": student,
                    "Attendance": status if isinstance(status, bool) else False,
                    "Remarks": str(remarks) if remarks is not None else ""
                })

            df = pd.DataFrame(rows)

            df = df.astype({
                "Student": "str",
                "Attendance": "bool",
                "Remarks": "str"
            })

            with st.form("attendance_form", border=False):
                edited_df = st.data_editor(
                    df,
                    hide_index=True,
                    width="stretch",
                    key=f"attendance_editor_{date_str}",
                    column_config={
                        "Student": st.column_config.TextColumn(
                            tr("Student"),
                            disabled=True
                        ),
                        "Attendance": st.column_config.CheckboxColumn(
                            tr("Attendance"),
                            required=True
                        ),
                        "Remarks": st.column_config.TextColumn(
                            tr("Remarks")
                        )
                    }
                )

                if st.form_submit_button(tr("Submit")):
                    payload = {}

                    for _, row in edited_df.iterrows():
                        payload[row["Student"]] = {
                            "0": bool(row["Attendance"]),
                            "1": row["Remarks"]
                        }

                    firebase.editAttendance(
                        id_token=userToken,
                        className=st.session_state["selected_class"],
                        field=date_str,
                        value=payload
                    )

                    st.success(tr("Attendance updated successfully!"))
            
    with schedule:
        with st.container(horizontal=True, vertical_alignment="center"):
            if st.button(tr("Edit"), type="secondary", icon=":material/edit:"):
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
                                    tr("Day"),
                                ),
                                "Start Time": st.column_config.TimeColumn(
                                    tr("Start Time"),
                                    format="hh:mm A",
                                ),
                                "End Time": st.column_config.TimeColumn(
                                    tr("End Time"),
                                    format="hh:mm A",
                                ),
                                "Activity": st.column_config.TextColumn(tr("Activity"))
                            }
                        )
        else:
            st.error(tr("Failed to retrieve class schedule."))

    with people:
        if class_data:
            st.subheader(tr("Coach"))
            with st.container(horizontal=True, vertical_alignment="center", border=True):
                st.write(st.session_state['profile']['name'])
            st.subheader(tr("Students"))
            try:
                for i in class_data["students"]:
                    with st.container(horizontal=True, vertical_alignment="center", border=True):
                        st.write(i.split()[1])
                        action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=[tr("Remove Student")], key=f"menu{i[0]}")
                        if action == tr("Remove Student"):
                            firebase.leaveClass(userToken, st.session_state['selected_class'], i)
            except:
                st.write(tr("No students found"))
        else:
            st.error(tr("Failed to retrieve class members."))

    with reports:
        # show a graph depicting class attendance
        with st.expander(f":material/assignment: {tr('Attendance Report')}"):
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
                df = pd.DataFrame(
                    list(attendance_report_dict.items()),
                    columns=[tr("Date"), tr("Number of Students")],
                )

                with st.container(border=True):
                    st.bar_chart(
                        df,
                        x=tr("Date"),
                        y=tr("Number of Students"),
                        color=tr("Number of Students"),
                    )
                with st.container(border=True):
                    st.text(tr("Class Attendance Rate"))
                    st.subheader(f"{round((total_attendance/max_attendance)*100, 2)}%")
                with st.container(border=True):
                    st.text(tr("Individual Student Attendance"))
                    st.dataframe(pd.DataFrame(list(individual_attendance.items()), columns=[tr("Student"), tr("Number of Classes Attended")]))

            except:
                st.write(tr("No attendance data yet."))

        with st.expander(f":material/school: {tr('Academic Report')}"):
            grades = firebase.getClassReports(userToken, st.session_state["selected_class"])
            # show each students name with expandable arrow to show their grades for each activity
            for i in grades:
                with st.expander(i.split()[1]):
                    #find and show TITLE FIRST of each activity and thier grades in a table
                    activity_grades = []
                    for j in grades[i]:
                        activity_grades.append([grades[i][j]["title"], grades[i][j]["grade"]])
                    st.dataframe(pd.DataFrame(activity_grades, columns=[tr("Activity"), tr("Grade")]), width="stretch", use_container_width=True)

            




if not st.session_state['class_view']:
    st.title(f"{tr('Welcome,')} {st.session_state['profile']['name']}")

    inbox_icon = (
        localized_asset_path("inbox_unread.png", language)
        if st.session_state["has_unread_announcement"]
        else localized_asset_path("inbox.png", language)
    )
    imageButtons("dashboards/coach/inbox.py", inbox_icon, 1646, 316)
    imageButtons(
        "dashboards/coach/roombooking.py",
        localized_asset_path("sroombooking.png", language),
        1646,
        465,
    )
    with st.container(horizontal=True, vertical_alignment="bottom"):
        st.subheader(tr("Your Classes"), width="content")
        st.divider()
    

            
    list_of_classes = firebase.getClasses(userToken)
    for i in list_of_classes.items():
        classCard(i)

    if st.button(tr("Create Class"), width="stretch", icon=":material/add:", type="primary"):
        createClass()

else:
    if st.session_state['activity_view']:
        activityViewer(st.session_state['activityDate'])
    else:
        classViewer()