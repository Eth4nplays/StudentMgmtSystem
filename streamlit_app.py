import streamlit as st
login = st.Page("login.py", title="School Activity Management System", icon=":material/school:")
admin = st.Page("dashboards/admin.py", title="Admin Dashboard", icon=":material/school:")
coach = st.Page("dashboards/coach.py", title="Coach Dashboard", icon=":material/school:")
student = st.Page("dashboards/student.py", title="Student Dashboard", icon=":material/school:")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = "None"

if st.session_state['logged_in'] == "None":
    st.navigation([login]).run()
elif st.session_state['logged_in'] == "Admin":
    st.navigation([admin]).run()
elif st.session_state['logged_in'] == "Coach":
    st.navigation([coach]).run()
elif st.session_state['logged_in'] == "Student":
    st.navigation([student]).run()
