import streamlit as st

st.page_link("dashboards/admin.py", label="Back", icon=":material/arrow_back:")
st.title("Manage Accounts")

coachTab, studentTab = st.tabs(["Coaches", "Students"])

with coachTab:
    st.write("hi")