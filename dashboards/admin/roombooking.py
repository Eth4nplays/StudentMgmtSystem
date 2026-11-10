import datetime
import streamlit as st
from helpers import cookies, firebase
from helpers.localization import normalize_language, translate

language = normalize_language(st.session_state["profile"].get("language"))
tr = lambda text: translate(text, language)

st.page_link("dashboards/admin.py", label=tr("Back"), icon=":material/arrow_back:")
st.title(tr("Room Booking"))

if cookies.getCookies("token") != None:
    userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

@st.dialog(tr("Add Room"))
def addRoom():
    with st.form("add_room_form"):
        roomName = st.text_input(tr("Room Name"))
        addRoom = st.form_submit_button(tr("Add Room"), type="primary", icon=":material/add:")

    if addRoom:
        roomName = roomName.strip()
        if not roomName:
            st.warning(tr("Please enter a room name."))
        elif any(character in roomName for character in ".$#[]/"):
            st.error(tr("Room names cannot contain . $ # [ ] or /."))
        else:
            result = firebase.createRoom(userToken, roomName)
            if result:
                st.success(f"{roomName} {tr('added successfully!')}")
                st.rerun()
            else:
                st.warning(tr("This room already exists."))

st.button(tr("Add Room"), on_click=addRoom, type="primary", icon=":material/add:")
    
bookingDate = st.date_input(
    tr("Select Date"),
    value=datetime.date.today(),
    format="DD/MM/YYYY",
    key="admin_room_booking_date",
    max_value=datetime.date.today()
)
dateKey = bookingDate.strftime("%Y-%m-%d")
rooms = firebase.getRooms(userToken)

if rooms is None:
    st.error(tr("Failed to retrieve rooms."))
else:
    bookings = firebase.getRoomBookings(userToken, dateKey)
    if bookings is None:
        st.error(tr("Failed to retrieve room bookings."))
    elif not rooms:
        st.info(tr("No rooms have been added yet."))
    else:
        for roomName in sorted(rooms):
            roomBookings = bookings.get(roomName, [])
            with st.container(border=True):
                st.subheader(roomName)
                if roomBookings:
                    for booking in roomBookings:
                        if booking.get("start") and booking.get("end"):
                            st.write(
                                f"**{booking['start']} - {booking['end']}** · "
                                f"{booking.get('coach', tr('Unknown coach'))}"
                                f" · {booking.get('class', tr('Unknown class'))}"
                            )
                else:
                    st.caption(tr("No bookings"))
