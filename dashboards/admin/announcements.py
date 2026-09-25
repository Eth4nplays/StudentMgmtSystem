import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
import datetime

st.page_link("dashboards/admin.py", label="Back", icon=":material/arrow_back:")
st.title("Announcements")

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

announcements = firebase.getAnnouncement(userToken)

@st.dialog("Create Announcement")
def createAnnouncement():
    contents, recepients = st.tabs(["Content", "Recepients"])
    with contents:
        title = st.text_input("Title")
        content = st.text_area("Contents")
        accounts = firebase.getAccounts(id_token=userToken)
    with recepients:
        studentList = []
        for i in accounts:
            if accounts[i]["role"] == "student":
                studentList.append(accounts[i]["name"])
        allStudents = st.checkbox("All Students", key="allStudents")
        students = st.multiselect("Students", studentList, disabled=allStudents)
        
        coachList = []
        for i in accounts:
            if accounts[i]["role"] == "coach":
                coachList.append(accounts[i]["name"])
        allCoaches = st.checkbox("All Coaches", key="allCoaches")
        coaches = st.multiselect("Coaches", coachList, disabled=allCoaches)
        
    
    if st.button("Submit", type="primary"):
        roles = []
        if allCoaches:
             roles.append("Coach")
        else:
             roles.extend(coaches)
        if allStudents:
            roles.append("Student")
        else:
            roles.extend(students)
        if title and roles and content:
            firebase.setAnnouncement(id_token=userToken, roles=roles, content=content, title=title, date=datetime.datetime.now().strftime("%y %m %d %H %M"))
            st.rerun()
        else:
             st.warning("Please input all fields")
        

@st.dialog("Delete account")
def deleteAnnouncement(title):
    st.write(f"Are you sure you want to delete {title}?")
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button("Yes"):
            firebase.deleteAnnouncement(title=title, id_token=userToken)
            st.rerun()
        elif st.button("No", type="primary"):
            st.rerun()


def announcementCard(title, contents):
    with st.container(border=True):

        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(contents["title"])
            st.write(f"Sent to {", ".join(contents["roles"])}")
            action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=["Delete Announcement"], key=f"menu{title}")
            if action == "Delete Announcement":
                deleteAnnouncement(title)
        st.write(contents["content"])
        st.caption(datetime.datetime.strptime(title, "%y %m %d %H %M").strftime("%d %B %Y, %I:%M %p"))
        

with st.container(horizontal=True, vertical_alignment="center", width="content"):
    if st.button("Create", type='primary', icon=":material/add:"):
            createAnnouncement()

    if st.button("Refresh", type='secondary', icon=":material/refresh:"):
            announcements = firebase.getAnnouncement(userToken)

if announcements != None:
    for date, contents in reversed(announcements.items()):
        announcementCard(date, contents)
else:
     st.write("No announcements yet.")