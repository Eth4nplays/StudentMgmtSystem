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

def classCard(i):
    with st.container(border=True):
        class_data = firebase.getClass(userToken, i[0])    

        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(i[0], width="content")
            st.caption(f"Coach: {firebase.getData(class_data["classOwner"], userToken)["name"]}")
            if st.button("Edit", type="secondary", icon=":material/edit:", key=f"editSchedule{i}"):
                editSchedule(class_data, i[0])
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

list_of_classes = firebase.getClasses(userToken)
for i in list_of_classes.items():
    classCard(i)