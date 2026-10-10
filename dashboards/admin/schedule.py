import streamlit as st
from io import StringIO
import pandas as pd
from helpers import cookies, firebase

st.page_link("dashboards/admin.py", label="Back", icon=":material/arrow_back:")
st.title("Schedules")
if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

def classCard(class_name, class_data, coach_name):
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(class_name, width="content")
            st.caption(f"Coach: {coach_name}")
            if st.button("Edit", type="secondary", icon=":material/edit:", key=f"editSchedule{class_name}"):
                editSchedule(class_data, class_name)
        if class_data:
            df = pd.read_csv(
                StringIO(class_data["classSchedule"].replace("\\n", "\n")),
                header=None,
                names=["Day", "Start Time", "End Time", "Activity"],
                skipinitialspace=True
            )

            st.dataframe(df, hide_index=True, width="stretch",             
                            column_config={
                                "Day": st.column_config.TextColumn(
                                    "Day",
                                ),
                                "Start Time": st.column_config.TimeColumn(
                                    "Start Time",
                                    format="hh:mm A",
                                ),
                                "End Time": st.column_config.TimeColumn(
                                    "End Time",
                                    format="hh:mm A",
                                ),
                                "Activity": st.column_config.TextColumn("Activity")
                            }
                        )
        else:
            st.error("Failed to retrieve class schedule.")

                

@st.dialog("Edit Schedule")
def editSchedule(class_data, selected_class):

    df = pd.read_csv(
        StringIO(class_data["classSchedule"].replace("\\n", "\n")),
        header=None,
        names=["Day", "Start Time", "End Time", "Activity"],
        skipinitialspace=True
    )

    for i in ["Start Time", "End Time"]:
        df[i] = pd.to_datetime(df[i], format="%H:%M:%S").dt.time

    edited = st.data_editor(
        df,
        hide_index=True,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "Day": st.column_config.SelectboxColumn(
                "Day",
                options=[
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday"
                ],
                required=True
            ),
            "Start Time": st.column_config.TimeColumn(
                "Start Time",
                format="hh:mm A",
                required=True
            ),
            "End Time": st.column_config.TimeColumn(
                "End Time",
                format="hh:mm A",
                required=True
            ),
            "Activity": st.column_config.TextColumn("Activity")
        }
    )

    if st.button("Submit"):
        newSchedule = edited.to_csv(
            index=False,
            header=False
        ).strip()
        result = firebase.editClass(
            userToken,
            selected_class,
            "classSchedule",
            newSchedule
        )
        if result:
            st.success("Schedule updated successfully!")
            st.rerun()
        else:
            st.error("Failed to update schedule.")

search_query = st.text_input(
    "Search schedules",
    placeholder="Search by class or coach name",
    icon=":material/search:",
).strip().casefold()

list_of_classes = firebase.getClasses(userToken)
if list_of_classes is None:
    st.error("Failed to retrieve class schedules.")
else:
    accounts = firebase.getAccounts(userToken) or {}
    matching_classes = []
    for class_name, class_data in list_of_classes.items():
        class_data = class_data or {}
        owner_id = class_data.get("classOwner")
        coach = accounts.get(owner_id) or {}
        coach_name = coach.get("name") or (
            f"Coach ({owner_id})" if owner_id else "Unassigned coach"
        )
        if (
            not search_query
            or search_query in class_name.casefold()
            or search_query in coach_name.casefold()
        ):
            matching_classes.append((class_name, class_data, coach_name))

    if not matching_classes:
        st.info("No schedules match your search.")
    else:
        for class_name, class_data, coach_name in matching_classes:
            classCard(class_name, class_data, coach_name)