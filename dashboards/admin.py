import streamlit as st
from helpers.cookies import *
from helpers.imagebuttons import *

st.title("Welcome, Admin")

imageButtons("dashboards/admin/manageAccounts.py", "assets/manage_accounts.png", 1646, 316)
col1, col2 = st.columns(2, wrap=False, width=340, gap="xxsmall")
with col1:
    imageButtons("dashboards/admin/schedule.py", "assets/schedule.png", 331*2.4, 316*2.4)
with col2:
    imageButtons("dashboards/admin/reports.py", "assets/reports.png", 331*2.4, 316*2.4)

imageButtons("dashboards/admin/announcements.py", "assets/announcements.png", 1646, 595)
imageButtons("dashboards/admin/activities.py", "assets/activities.png", 1646, 595)
imageButtons("dashboards/admin/roombooking.py", "assets/roombooking.png", 1646, 595)
