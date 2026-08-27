import streamlit as st
from helpers.cookies import *
import helpers.firebase as firebase

# App Pages
login = st.Page("login.py", title="School Activity Management System", icon=":material/school:")
admin = st.Page("dashboards/admin.py", title="Admin Dashboard", icon=":material/school:")
coach = st.Page("dashboards/coach.py", title="Coach Dashboard", icon=":material/school:")
student = st.Page("dashboards/student.py", title="Student Dashboard", icon=":material/school:")

# Checks login state and sends user to corresponding pages
if 'uid' not in st.session_state:
    st.session_state['uid'] = 'none'
if 'token' not in st.session_state:
    st.session_state['token'] = 'none'

cookie_manager.get_all("mainProfileGet")
profile = firebase.getRole(
            getCookies("uid"),
            getCookies("token")
        )
if profile == None:
    profile = firebase.getRole(
            st.session_state['uid'],
            st.session_state['token']
        )
    if profile == None:
        role = "none"
    else:
        role = profile["role"]
else:
    role = profile["role"]

if role == "admin":
    manageAccount = st.Page("dashboards/admin/manageAccounts.py", title="Manage Accounts", icon=":material/manage_accounts:")
    pg = st.navigation([admin, manageAccount])
    pg.run()
elif role == "coach":
    st.navigation([coach]).run()
elif role == "student":
    st.navigation([student]).run()
else:
    st.navigation([login]).run()

if role == "admin" or role == "coach" or role == "student":
    with st.sidebar:
        if st.button("Logout", icon=":material/logout:", key="logout"):
            logout()
