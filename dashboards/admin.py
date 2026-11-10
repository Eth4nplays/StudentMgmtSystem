import streamlit as st
from helpers.cookies import *
from helpers.imagebuttons import *
from helpers.localization import localized_asset_path, normalize_language, translate

language = normalize_language(st.session_state["profile"].get("language"))
st.title(translate("Welcome, Admin", language))

imageButtons("dashboards/admin/manageAccounts.py", localized_asset_path("manage_accounts.png", language), 1646, 316)
col1, col2 = st.columns(2, wrap=False, width=340, gap="xxsmall")
with col1:
    imageButtons("dashboards/admin/schedule.py", localized_asset_path("schedule.png", language), 331*2.4, 316*2.4)
with col2:
    imageButtons("dashboards/admin/reports.py", localized_asset_path("reports.png", language), 331*2.4, 316*2.4)

imageButtons("dashboards/admin/announcements.py", localized_asset_path("announcements.png", language), 1646, 595)
imageButtons("dashboards/admin/activities.py", localized_asset_path("activities.png", language), 1646, 595)
imageButtons("dashboards/admin/roombooking.py", localized_asset_path("roombooking.png", language), 1646, 595)
