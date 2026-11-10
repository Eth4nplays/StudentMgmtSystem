import streamlit as st
from helpers.cookies import *
import helpers.firebase as firebase
import firebase_admin
from firebase_admin import credentials
from helpers.imagebuttons import encodeImage
from helpers.information import infobox
from helpers.localization import LANGUAGES, normalize_language, translate

st.set_option("client.toolbarMode", "viewer")
login = st.Page("login.py", title="School Activity Management System", icon=":material/school:")

# Gets authentication information and get user role
if 'uid' not in st.session_state:
    st.session_state['uid'] = 'none'
if 'token' not in st.session_state:
    st.session_state['token'] = 'none'

# get the user profile and save it in session state
cookie_manager.get_all("mainProfileGet")
if 'profile' not in st.session_state:
    profile = firebase.getData(
                getCookies("uid"),
                getCookies("token")
            )
    st.session_state['profile'] = profile
profile = st.session_state['profile']
if profile == None:
    profile = firebase.getData(
            st.session_state['uid'],
            st.session_state['token']
        )
    st.session_state['profile'] = profile
    if profile == None:
        role = "none"
    else:
        role = profile["role"]
else:
    role = profile["role"]

language = normalize_language(profile.get("language")) if role in {"student", "coach", "admin"} else "en"
if role in {"student", "coach", "admin"}:
    with st.sidebar:
        selected_language = st.selectbox(
            translate("Language", language),
            options=list(LANGUAGES),
            index=list(LANGUAGES).index(language),
            format_func=lambda value: LANGUAGES[value],
            key=f"language_{getCookies('uid') or st.session_state['uid']}",
        )

    if selected_language != language:
        uid = getCookies("uid") or st.session_state["uid"]
        user_token = getCookies("token") or st.session_state["token"]
        if firebase.setUserLanguage(uid, user_token, selected_language):
            profile["language"] = selected_language
            st.session_state["profile"] = profile
            st.rerun()
        else:
            st.sidebar.error(translate("Unable to save language preference.", language))

# Based on user role, send user to corresponding pages
# page declaration is added here becasue to ensure that users of other roles cant access restricted pages 
if role == "admin":
    admin = st.Page("dashboards/admin.py", title=translate("Dashboard", language), icon=":material/school:")
    manageAccount = st.Page("dashboards/admin/manageAccounts.py", title=translate("Manage Accounts", language), icon=":material/manage_accounts:")
    announcements = st.Page("dashboards/admin/announcements.py", title=translate("Announcements", language), icon=":material/campaign:")
    reports = st.Page("dashboards/admin/reports.py", title=translate("Reports", language), icon=":material/analytics:")
    schedule = st.Page("dashboards/admin/schedule.py", title=translate("Schedules", language), icon=":material/calendar_month:")
    activities = st.Page("dashboards/admin/activities.py", title=translate("Activities", language), icon=":material/directions_run:")
    roombooking = st.Page("dashboards/admin/roombooking.py", title=translate("Room Booking", language), icon=":material/meeting_room:")

    pg = st.navigation({translate("Admin", language): [admin, manageAccount, announcements], translate("Classes", language): [reports, schedule, activities, roombooking]})
    pg.run()
elif role == "coach":
    coach = st.Page("dashboards/coach.py", title=translate("Dashboard", language), icon=":material/school:")
    coachInbox = st.Page("dashboards/coach/inbox.py", title=translate("Inbox", language), icon=":material/inbox:")
    roombookingCoach = st.Page("dashboards/coach/roombooking.py", title=translate("Room Booking", language), icon=":material/meeting_room:")
    attendanceScanner = st.Page(
        "dashboards/coach/attendancescan.py",
        title="Attendance Scanner",
        visibility="hidden",
    )
    pg = st.navigation({translate("Coach", language): [coach, coachInbox, roombookingCoach, attendanceScanner]})
    pg.run()
elif role == "student":
    student = st.Page("dashboards/student.py", title=translate("Dashboard", language), icon=":material/school:")
    studentInbox = st.Page("dashboards/student/inbox.py", title=translate("Inbox", language), icon=":material/inbox:")
    pg = st.navigation({translate("Student/Parent", language): [student, studentInbox]})
    pg.run()
else:
    st.navigation([login]).run()

# sidebar contents for all logged in users
if role == "admin" or role == "coach" or role == "student":
    with st.sidebar:
        # show the logo on the top of sidebar
        st.markdown(
            f"""
            <style>
                [data-testid="stSidebarNav"]::before {{
                    content: "";
                    display: block;
                    width: 250px;
                    height: 150px;
                    margin-bottom: 20px;

                    background-image: url({encodeImage("assets/logo.png")});
                    background-size: contain;
                    background-repeat: no-repeat;
                    background-position: center;
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        with st.container(horizontal=True):
            if st.button(translate("Logout", language), icon=":material/logout:", key="logout"):
                logout()
            infobox(preset=role, text=translate("Guide", language), icon=":material/info:")

# initialize firebase admin if the user is logged in as an admin
if role == "admin":
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            {
                "type": st.secrets["firebase_admin"]["type"],
                "project_id": st.secrets["firebase_admin"]["project_id"],
                "private_key_id": st.secrets["firebase_admin"]["private_key_id"],
                "private_key": st.secrets["firebase_admin"]["private_key"],
                "client_email": st.secrets["firebase_admin"]["client_email"],
                "client_id": st.secrets["firebase_admin"]["client_id"],
                "token_uri": st.secrets["firebase_admin"]["token_uri"],
            }
        )

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": st.secrets["firebase"]["database_url"],
            },
        )