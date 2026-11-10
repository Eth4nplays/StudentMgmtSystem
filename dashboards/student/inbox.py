import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
import datetime
from helpers.localization import localized_month_name, normalize_language, translate

language = normalize_language(st.session_state["profile"].get("language"))
tr = lambda text: translate(text, language)

st.page_link("dashboards/student.py", label=tr("Back"), icon=":material/arrow_back:")
st.title(tr("Inbox"))

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

if cookies.getCookies("uid") != None:
        uid = cookies.getCookies("uid")
else:
    uid = st.session_state['uid']

announcements = firebase.getAnnouncement(userToken)

def announcementCard(title, contents, unread):
    with st.container(border=True):

        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(contents["title"])
            if unread:
                st.badge(tr("Unread"), color="red")
        st.markdown(contents["content"])
        posted_at = datetime.datetime.strptime(title, "%y %m %d %H %M")
        st.caption(
            f"{posted_at.day:02d} {localized_month_name(posted_at.month, language)} "
            f"{posted_at.year}, {posted_at.strftime('%I:%M %p')}"
        )

with st.container(horizontal=True, vertical_alignment="center", width="content"):

    refresh_clicked = st.button(tr("Refresh"), type='secondary', icon=":material/refresh:")

    available_announcements = {
        date: contents
        for date, contents in (announcements or {}).items()
        if "Student" in contents.get("roles", [])
        or st.session_state['profile']['name'] in contents.get("roles", [])
    }
    latest_announcement = max(
        available_announcements,
        key=lambda date: datetime.datetime.strptime(date, "%y %m %d %H %M"),
        default=None
    )

    if st.button(
        tr("Mark all as read"),
        type="secondary",
        icon=":material/done_all:",
        disabled=latest_announcement is None
    ):
        if firebase.setLastReadAnnouncement(uid, userToken, latest_announcement):
            st.session_state['profile']['lastread'] = latest_announcement
            st.session_state['profile']['lastreadannouncement'] = latest_announcement
            st.session_state["has_unread_announcement"] = False
            st.rerun()
        else:
            st.error(tr("Failed to mark announcements as read."))

last_read = (
    st.session_state['profile'].get("lastreadannouncement")
    or st.session_state['profile'].get("lastread")
)
last_read_datetime = (
    datetime.datetime.strptime(last_read, "%y %m %d %H %M")
    if last_read
    else None
)
latest_announcement_datetime = (
    datetime.datetime.strptime(latest_announcement, "%y %m %d %H %M")
    if latest_announcement
    else None
)
has_unread_announcement = (
    latest_announcement_datetime is not None
    and (
        last_read_datetime is None
        or latest_announcement_datetime > last_read_datetime
    )
)
if refresh_clicked:
    st.session_state["has_unread_announcement"] = has_unread_announcement

if available_announcements:
    for date, contents in reversed(list(available_announcements.items())):
        announcement_datetime = datetime.datetime.strptime(date, "%y %m %d %H %M")
        is_unread = last_read_datetime is None or announcement_datetime > last_read_datetime
        announcementCard(date, contents, is_unread)
else:
     st.write(tr("No announcements available."))
