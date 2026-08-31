import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from datetime import datetime


if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

announcements = firebase.getAnnouncement(userToken)

def announcementCard(title, contents):
    with st.container(border=True):

        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(contents["title"])
            st.write(f"{", ".join(contents["roles"])}")
        st.write(contents["content"])
        

with st.container(horizontal=True, vertical_alignment="center", width="content"):

    if st.button("Refresh", type='secondary', icon=":material/refresh:"):
            announcements = firebase.getAnnouncement(userToken)

if announcements != None:
    for date, contents in reversed(announcements.items()):
        announcementCard(date, contents)
else:
     st.write("No announcements yet.")
