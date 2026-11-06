import pandas as pd
import qrcode
import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from io import BytesIO

st.page_link("dashboards/admin.py", label="Back", icon=":material/arrow_back:")

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

def fetchAccounts():
    return firebase.getAccounts(id_token=userToken)

@st.dialog("Upload Accounts csv")
def accountbulkupload():
    st.download_button("Download CSV Template", data="name,email,password,role\nJohn Doe,john.doe@example.com,Abc123,student\nJane Smith,jane.smith@example.com,Abc123,coach", file_name="account_template.csv", mime="text/csv")

    accountbulkcsv = st.file_uploader("Upload CSV", type = "csv")
    if accountbulkcsv is not None:
        dataframe = pd.read_csv(accountbulkcsv)

        st.spinner("Uploading accounts...")

        for i in range(len(dataframe)):
            name = str(dataframe.iloc[i]["name"])
            email = str(dataframe.iloc[i]["email"])
            password = str(dataframe.iloc[i]["password"])
            role = str(dataframe.iloc[i]["role"])
            if name and email and password and role:
                if role not in ["student", "coach"]:
                    if role.lower() == "teacher":
                        role = "coach"
                    if role.lower() == "parent":
                        role = "student"
                newAccount = firebase.createAccount(email=email.strip(), password=password.strip())
                firebase.setData(uid=newAccount["localId"], id_token=newAccount["idToken"], role=role.lower(), name=name, email=email.strip())
        st.rerun()
        
@st.dialog("QR Code")
def showqr(selectUid, name):
    st.write("You may print this QR code for students/coaches")
    qrData = f"{selectUid} {name}"

    qr_img = qrcode.make(qrData)
    img = qr_img._img

    st.image(img)

    buf = BytesIO()
    img.save(buf, format="JPEG")
    byte_im = buf.getvalue()
    

    st.download_button(
        label="Download QR Code",
        data=byte_im,
        file_name=f"{name}-QR.png",
        mime="image/png"
    )

@st.dialog("Create account")
def createAccount():
    user_types = {
    "Coach": "coach",
    "Student/Parent": "student"
    }

    selected = st.segmented_control(
        "User Type",
        options=list(user_types.keys()),
        default="Coach"
    )

    accType = user_types[selected]
    accName = st.text_input("Name")
    accEmail = st.text_input("Email", validate=("^[^@]+@[^@]+.[^@]+$", "Must be a valid email"))
    accPassword = st.text_input("Temporary Password", validate=("^.{6,}$", "Password must have 6 characters"))
    if st.button("Create Account", type="primary"):
        if accType!="" and accEmail!="" and accName!="" and accPassword!="":
            newAccount = firebase.createAccount(email=accEmail.strip(), password=accPassword.strip())
            firebase.setData(uid=newAccount["localId"], id_token=newAccount["idToken"], role=accType, name=accName, email=accEmail.strip())
            st.rerun()
        else:
            st.error("All of the fields must be filled in before creating an account")

@st.dialog("Delete account")
def deleteAccount(accName, uid):
    st.write(f"Are you sure you want to delete {accName}?")
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button("Yes"):
            firebase.deleteAccount(uid=uid)
            firebase.deleteData(uid=uid, id_token=userToken)
            st.rerun()
        elif st.button("No", type="primary"):
            st.rerun()
@st.dialog("Reset Password")
def resetAccountPassword(accEmail):
     st.write(f"Are you sure you want to reset {accEmail}?")
     with st.container(horizontal=True, vertical_alignment="center"):
             if st.button("Yes"):
                 firebase.resetPassword(accEmail)
                 st.rerun()
             elif st.button("No", type="primary"):
                 st.rerun()

def accountCard(uid, account):
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(account["name"])
            st.write(account["email"])
            action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=["Delete Account","Reset Password", "Show QR"], key=f"menu{account["name"]}")
            if action == "Delete Account":
                deleteAccount(account["name"], uid)
            if action == "Reset Password":
                resetAccountPassword(account["email"])
            if action == "Show QR":
                showqr(uid, account["name"])
        st.caption(uid)

accounts = fetchAccounts()

st.title("Manage Accounts")

with st.container(horizontal=True, vertical_alignment="center", width="content"):
    if st.button("Create", type='primary', icon=":material/add:"):
            createAccount()
    if st.button("Upload", type='primary', icon=":material/upload:"):
            accountbulkupload()

    if st.button("Refresh", type='secondary', icon=":material/refresh:"):
            accounts = fetchAccounts()

search_query = st.text_input(
    "Search accounts",
    placeholder="Search by name, email, or user ID",
    icon=":material/search:",
).strip().casefold()

accounts = accounts or {}
coachTab, studentTab = st.tabs(["Coaches", "Students/Parents"])

with coachTab:
    for uid, account in accounts.items():
        if account["role"] == "coach" and (
            not search_query
            or search_query in account["name"].casefold()
            or search_query in account["email"].casefold()
            or search_query in uid.casefold()
        ):
            accountCard(uid, account)
with studentTab:
    for uid, account in accounts.items():
        if account["role"] == "student" and (
            not search_query
            or search_query in account["name"].casefold()
            or search_query in account["email"].casefold()
            or search_query in uid.casefold()
        ):
            accountCard(uid, account)