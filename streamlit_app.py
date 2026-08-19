import streamlit as st

# App Pages
login = st.Page("login.py", title="School Activity Management System", icon=":material/school:")
admin = st.Page("dashboards/admin.py", title="Admin Dashboard", icon=":material/school:")
coach = st.Page("dashboards/coach.py", title="Coach Dashboard", icon=":material/school:")
student = st.Page("dashboards/student.py", title="Student Dashboard", icon=":material/school:")

if 'role' not in st.query_params:
    st.query_params['role'] = 'none'

# Checks login state and sends user to corresponding pages
role = st.query_params["role"]
if role == "admin":
    st.navigation([admin]).run()
elif role == "coach":
    st.navigation([coach]).run()
elif role == "student":
    st.navigation([student]).run()
else:
    st.navigation([login]).run()