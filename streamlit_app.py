import streamlit as st

# App Pages
login = st.Page("login.py", title="School Activity Management System", icon=":material/school:")
admin = st.Page("dashboards/admin.py", title="Admin Dashboard", icon=":material/school:")
coach = st.Page("dashboards/coach.py", title="Coach Dashboard", icon=":material/school:")
student = st.Page("dashboards/student.py", title="Student Dashboard", icon=":material/school:")

if 'logged_in' not in st.query_params:
    st.query_params['logged_in'] = "None"

# Checks login state and sends user to corresponding pages
if st.query_params['logged_in'] == "None":
    st.navigation([login]).run()
elif st.query_params['logged_in'] == "Admin":
    st.navigation([admin]).run()
elif st.query_params['logged_in'] == "Coach":
    st.navigation([coach]).run()
elif st.query_params['logged_in'] == "Student":
    st.navigation([student]).run()
