import datetime
import streamlit as st
from helpers import cookies, firebase

st.page_link("dashboards/coach.py", label="Back", icon=":material/arrow_back:")

st.title("Room Booking")

if cookies.getCookies("token") != None:
    userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

if cookies.getCookies("uid") != None:
    uid = cookies.getCookies("uid")
else:
    uid = st.session_state['uid']

@st.dialog("Book a Room")
def bookRoomDialog(defaultDate):
    class_data = firebase.getClasses(userToken)
    classNames = []
    if class_data:
        for className, classInfo in class_data.items():
            if uid in classInfo.get("classOwner", ""):
                classNames.append(className)

    if not classNames:
        st.info("You do not have any classes to book a room for.")
        return

    selectedClass = st.selectbox(
        "Select Class",
        sorted(classNames),
        key="room_booking_class"
    )
    bookingDate = st.date_input(
        "Booking Date",
        value=defaultDate,
        format="DD/MM/YYYY",
        key="room_dialog_date"
    )
    with st.container(horizontal=True):
        startTime = st.time_input(
            "Start Time",
            value=datetime.time(9, 0),
            key="room_dialog_start"
        )
        endTime = st.time_input(
            "End Time",
            value=datetime.time(10, 0),
            key="room_dialog_end"
        )

    dateKey = bookingDate.strftime("%Y-%m-%d")
    rooms = firebase.getRooms(userToken)
    bookings = firebase.getRoomBookings(userToken, dateKey)

    if rooms is None or bookings is None:
        st.error("Failed to retrieve room bookings.")
    elif not rooms:
        st.info("No rooms have been added yet.")
    elif endTime <= startTime:
        st.warning("The end time must be after the start time.")
    else:
        startKey = startTime.strftime("%H:%M")
        endKey = endTime.strftime("%H:%M")
        availableRooms = []
        for roomName in sorted(rooms):
            roomBookings = bookings.get(roomName, [])
            isAvailable = True
            with st.container(border=True):
                st.subheader(roomName)
                if roomBookings:
                    for booking in roomBookings:
                        if booking.get("start") and booking.get("end"):
                            st.caption(
                                f"{booking['start']} - {booking['end']} · "
                                f"{booking.get('coach', 'Unknown coach')} · "
                                f"{booking.get('class', 'Unknown class')}"
                            )
                            if startKey < booking["end"] and endKey > booking["start"]:
                                isAvailable = False
                        else:
                            st.caption("Booked (time unavailable)")
                            isAvailable = False
                else:
                    st.caption("No bookings")

                if isAvailable:
                    availableRooms.append(roomName)

        if availableRooms:
            selectedRoom = st.selectbox(
                "Select an available room",
                availableRooms,
                key="room_dialog_selected_room"
            )
            if st.button("Book Room", type="primary", icon=":material/meeting_room:"):
                result = firebase.bookRoom(
                    userToken,
                    selectedRoom,
                    dateKey,
                    startKey,
                    endKey,
                    st.session_state['profile']['name'],
                    selectedClass
                )
                if result:
                    st.success(f"{selectedRoom} booked successfully!")
                    st.rerun()
                else:
                    st.warning("This time is no longer available. Please select a different time or room.")
        else:
            st.info("No rooms are available for this time. Please select another time.")



bookingDate = st.date_input(
    "Select Date",
    value=datetime.date.today(),
    format="DD/MM/YYYY",
    key="coach_room_booking_date"
)
dateKey = bookingDate.strftime("%Y-%m-%d")
rooms = firebase.getRooms(userToken)

if st.button("Book a Room", type="primary", icon=":material/meeting_room:"):
    bookRoomDialog(bookingDate)

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
                                f"{booking['start']} - {booking['end']} · "
                                f"{booking.get('coach', 'Unknown coach')}"
                            )
                            st.caption(f"Class: {booking.get('class', 'Unknown class')}")
                        else:
                            st.write(f"Booked by: {booking.get('coach', 'Unknown coach')}")
                            st.caption(f"Class: {booking.get('class', 'Unknown class')}")
                else:
                    st.caption("No bookings")
