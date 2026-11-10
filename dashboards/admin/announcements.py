import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
import datetime
from helpers.localization import localized_month_name, normalize_language, translate

language = normalize_language(st.session_state["profile"].get("language"))
tr = lambda text: translate(text, language)

st.page_link("dashboards/admin.py", label=tr("Back"), icon=":material/arrow_back:")
st.title(tr("Announcements"))

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

announcements = firebase.getAnnouncement(userToken)

@st.dialog(tr("Create Announcement"))
def createAnnouncement():
    contents, recepients = st.tabs([tr("Content"), tr("Recepients")])
    with contents:
        title = st.text_input(tr("Title"))
        content = st.text_area(tr("Contents"))
        accounts = firebase.getAccounts(id_token=userToken)
    with recepients:
        studentList = []
        for i in accounts:
            if accounts[i]["role"] == "student":
                studentList.append(accounts[i]["name"])
        allStudents = st.checkbox(tr("All Students"), key="allStudents")
        students = st.multiselect(tr("Students"), studentList, disabled=allStudents)
        
        coachList = []
        for i in accounts:
            if accounts[i]["role"] == "coach":
                coachList.append(accounts[i]["name"])
        allCoaches = st.checkbox(tr("All Coaches"), key="allCoaches")
        coaches = st.multiselect(tr("Coaches"), coachList, disabled=allCoaches)
        
    
    if st.button(tr("Submit"), type="primary"):
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
             st.warning(tr("Please input all fields"))
        

@st.dialog(tr("Delete Announcement?"))
def deleteAnnouncement(title):
    st.write(f"{tr('Are you sure you want to delete')} {title}?")
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button(tr("Yes")):
            firebase.deleteAnnouncement(title=title, id_token=userToken)
            st.rerun()
        elif st.button(tr("No"), type="primary"):
            st.rerun()


def announcementCard(title, contents):
    with st.container(border=True):

        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(contents["title"])
            st.write(f"{tr('Sent to')} {', '.join(tr(role) for role in contents['roles'])}")
            action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=[tr("Delete Announcement")], key=f"menu{title}")
            if action == tr("Delete Announcement"):
                deleteAnnouncement(title)
        st.markdown(contents["content"])
        posted_at = datetime.datetime.strptime(title, "%y %m %d %H %M")
        st.caption(f"{posted_at.day:02d} {localized_month_name(posted_at.month, language)} {posted_at.year}, {posted_at.strftime('%I:%M %p')}")
        

with st.container(horizontal=True, vertical_alignment="center", width="content"):
    if st.button(tr("Create"), type='primary', icon=":material/add:"):
            createAnnouncement()

    if st.button(tr("Refresh"), type='secondary', icon=":material/refresh:"):
            announcements = firebase.getAnnouncement(userToken)

if announcements != None:
    for date, contents in reversed(announcements.items()):
        announcementCard(date, contents)
else:
     st.write(tr("No announcements yet."))