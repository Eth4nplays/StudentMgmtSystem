import pandas as pd
import streamlit as st

import helpers.cookies as cookies
import helpers.firebase as firebase
from helpers.localization import normalize_language, translate

language = normalize_language(st.session_state["profile"].get("language"))
tr = lambda text: translate(text, language)

if cookies.getCookies("token") is not None:
    userToken = cookies.getCookies("token")
else:
    userToken = st.session_state["token"]


def display_name(student):
    return student.split(" ", 1)[-1]


def show_attendance_report(class_data):
    attendance = class_data.get("attendance") or {}
    students = class_data.get("students") or []
    attendance_by_date = []
    total_present = 0
    total_records = 0
    student_rows = []

    for student in students:
        name = display_name(student)
        records = [
            (day_records or {})[name]
            for day_records in attendance.values()
            if name in (day_records or {})
        ]
        present = sum(bool(record) for record in records)
        student_rows.append({
            tr("Student"): name,
            tr("Days Attended"): present,
            tr("Days Recorded"): len(records),
            tr("Attendance Rate"): f"{present / len(records) * 100:.1f}%" if records else "—",
        })

    for date, day_records in attendance.items():
        day_records = day_records or {}
        present = sum(bool(attended) for attended in day_records.values())
        attendance_by_date.append({tr("Date"): date, tr("Students Present"): present})
        total_present += present
        total_records += len(day_records)

    if not attendance_by_date:
        st.info(tr("No attendance data recorded for this class yet."))
        return

    #make a bar chart of attendance by date with border
    st.bar_chart(pd.DataFrame(attendance_by_date), x=tr("Date"), y=tr("Students Present"))
    attendance_rate = total_present / total_records * 100 if total_records else 0
    rate_column, records_column = st.columns(2)
    rate_column.metric(tr("Class Attendance Rate"), f"{attendance_rate:.1f}%")
    records_column.metric(tr("Attendance Records"), f"{total_present}/{total_records} {tr('present')}")
    if student_rows:
        st.dataframe(pd.DataFrame(student_rows), width="stretch", hide_index=True)


def show_academic_report(class_name, class_data):
    reports = firebase.getClassReports(userToken, class_name)
    if reports is None:
        st.error(tr("Failed to retrieve assignment reports."))
        return

    if not reports:
        st.info(tr("No students or assignments found in this class."))
        return

    tasks = class_data.get("tasks") or {}
    for student in sorted(reports, key=lambda item: display_name(item).casefold()):
        with st.expander(display_name(student)):
            student_reports = reports[student]
            if not student_reports:
                st.info(tr("No assignments found for this student."))
                continue

            rows = []
            for task_id, report in student_reports.items():
                task = tasks.get(task_id) or {}
                submission = (task.get("submissions") or {}).get(student) or {}
                grade = report.get("grade")
                if grade == "Not submitted":
                    grade_text = tr("Not submitted")
                    submission_status = tr("Not submitted")
                elif grade is None:
                    grade_text = tr("Not graded")
                    submission_status = tr("Submitted")
                else:
                    grade_text = f"{grade} / {report.get('totalGrade', '—')}"
                    submission_status = tr("Submitted")

                rows.append({
                    tr("Assignment"): report.get("title", task_id),
                    tr("Grade"): grade_text,
                    tr("Submission"): submission_status,
                    tr("Coach Feedback"): submission.get("comment") or "—",
                })

            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


st.page_link("dashboards/admin.py", label=tr("Back"), icon=":material/arrow_back:")
st.title(tr("Reports"))

classes = firebase.getClasses(userToken)
if classes is None:
    st.error(tr("Failed to retrieve classes."))
else:
    accounts = firebase.getAccounts(userToken) or {}
    classes_by_coach = {}
    for class_name, class_data in classes.items():
        class_data = class_data or {}
        owner_id = class_data.get("classOwner")
        classes_by_coach.setdefault(owner_id, []).append((class_name, class_data))

    if not classes_by_coach:
        st.info(tr("No class reports are available yet."))
    else:
        def coach_label(owner_id):
            if owner_id is None:
                return tr("Unassigned coach")
            coach = accounts.get(owner_id) or {}
            return coach.get("name") or f"Coach ({owner_id})"

        for owner_id in sorted(
            classes_by_coach,
            key=lambda key: coach_label(key).casefold(),
        ):
            with st.expander(coach_label(owner_id)):
                for class_name, class_data in sorted(
                    classes_by_coach[owner_id],
                    key=lambda item: item[0].casefold(),
                ):
                    with st.expander(class_name):
                        attendance_tab, academic_tab = st.tabs(
                            [f":material/assignment: {tr('Attendance')}", f":material/school: {tr('Academic')}"]
                        )
                        with attendance_tab:
                            show_attendance_report(class_data)
                        with academic_tab:
                            show_academic_report(class_name, class_data)
