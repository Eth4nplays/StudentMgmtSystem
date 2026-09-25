import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
import datetime

st.page_link("dashboards/student.py", label="Back", icon=":material/arrow_back:")
st.title("Inbox")

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

announcements = firebase.getAnnouncement(userToken)

def announcementCard(title, contents):
    with st.container(border=True):

        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(contents["title"])
        st.markdown(contents["content"])
        st.caption(datetime.datetime.strptime(title, "%y %m %d %H %M").strftime("%d %B %Y, %I:%M %p"))

with st.container(horizontal=True, vertical_alignment="center", width="content"):

    if st.button("Refresh", type='secondary', icon=":material/refresh:"):
            announcements = firebase.getAnnouncement(userToken)

if announcements != None:
    for date, contents in reversed(announcements.items()):
        if "Student" in contents["roles"] or st.session_state['profile']['name'] in contents["roles"]:    
            announcementCard(date, contents)
else:
     st.write("No announcements yet.")
