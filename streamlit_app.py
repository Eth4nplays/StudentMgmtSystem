import streamlit as st
login = st.Page("login.py", title="Create entry", icon=":material/add_circle:")
admin = st.Page("admin.py", title="Create entry", icon=":material/add_circle:")
coach = st.Page("coach.py", title="Create entry", icon=":material/add_circle:")
student = st.Page("student.py", title="Create entry", icon=":material/add_circle:")

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
