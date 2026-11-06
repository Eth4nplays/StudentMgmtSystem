import datetime
import streamlit as st
from helpers import cookies, firebase

st.page_link("dashboards/admin.py", label="Back", icon=":material/arrow_back:")
st.title("Room Booking")

if cookies.getCookies("token") != None:
    userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

@st.dialog("Add Room")
def addRoom():
    with st.form("add_room_form"):
        roomName = st.text_input("Room Name")
        addRoom = st.form_submit_button("Add Room", type="primary", icon=":material/add:")

    if addRoom:
        roomName = roomName.strip()
        if not roomName:
            st.warning("Please enter a room name.")
        elif any(character in roomName for character in ".$#[]/"):
            st.error("Room names cannot contain . $ # [ ] or /.")
        else:
            result = firebase.createRoom(userToken, roomName)
            if result:
                st.success(f"{roomName} added successfully!")
                st.rerun()
            else:
                st.warning("This room already exists.")

st.button("Add Room", on_click=addRoom, type="primary", icon=":material/add:")
    
bookingDate = st.date_input(
    "Select Date",
    value=datetime.date.today(),
    format="DD/MM/YYYY",
    key="admin_room_booking_date",
    max_value=datetime.date.today()
)
dateKey = bookingDate.strftime("%Y-%m-%d")
rooms = firebase.getRooms(userToken)

if rooms is None:
    st.error("Failed to retrieve rooms.")
else:
    bookings = firebase.getRoomBookings(userToken, dateKey)
    if bookings is None:
        st.error("Failed to retrieve room bookings.")
    elif not rooms:
        st.info("No rooms have been added yet.")
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
                                f"{booking.get('coach', 'Unknown coach')}"
                                f" · {booking.get('class', 'Unknown class')}"
                            )
                else:
                    st.caption("No bookings")
