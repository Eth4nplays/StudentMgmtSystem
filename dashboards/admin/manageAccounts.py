import pandas as pd
import qrcode
import streamlit as st
import helpers.firebase as firebase
import helpers.cookies as cookies
from io import BytesIO
from helpers.localization import normalize_language, translate

language = normalize_language(st.session_state["profile"].get("language"))
tr = lambda text: translate(text, language)

st.page_link("dashboards/admin.py", label=tr("Back"), icon=":material/arrow_back:")

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

def fetchAccounts():
    return firebase.getAccounts(id_token=userToken)

@st.dialog(tr("Upload Accounts csv"))
def accountbulkupload():
    st.download_button(tr("Download CSV Template"), data="name,email,password,role\nJohn Doe,john.doe@example.com,Abc123,student\nJane Smith,jane.smith@example.com,Abc123,coach", file_name="account_template.csv", mime="text/csv")

    accountbulkcsv = st.file_uploader(tr("Upload CSV"), type = "csv")
    if st.button(tr("Upload"), type='primary', icon=":material/upload:"):
        if accountbulkcsv is not None:
            dataframe = pd.read_csv(accountbulkcsv)
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
        
@st.dialog(tr("QR Code"))
def showqr(selectUid, name):
    st.write(tr("You may print this QR code for students/coaches"))
    qrData = f"{selectUid} {name}"

    qr_img = qrcode.make(qrData)
    img = qr_img._img

    st.image(img)

    buf = BytesIO()
    img.save(buf, format="JPEG")
    byte_im = buf.getvalue()
    

    st.download_button(
        label=tr("Download QR Code"),
        data=byte_im,
        file_name=f"{name}-QR.png",
        mime="image/png"
    )

@st.dialog(tr("Create account"))
def createAccount():
    user_types = {
    tr("Coach"): "coach",
    tr("Student/Parent"): "student"
    }

    selected = st.segmented_control(
        tr("User Type"),
        options=list(user_types.keys()),
        default=tr("Coach")
    )

    accType = user_types[selected]
    accName = st.text_input(tr("Name"))
    accEmail = st.text_input(tr("Email"), validate=("^[^@]+@[^@]+.[^@]+$", tr("Must be a valid email")))
    accPassword = st.text_input(tr("Temporary Password"), validate=("^.{6,}$", tr("Password must have 6 characters")))
    if st.button(tr("Create Account"), type="primary"):
        if accType!="" and accEmail!="" and accName!="" and accPassword!="":
            newAccount = firebase.createAccount(email=accEmail.strip(), password=accPassword.strip())
            firebase.setData(uid=newAccount["localId"], id_token=newAccount["idToken"], role=accType, name=accName, email=accEmail.strip())
            st.rerun()
        else:
            st.error(tr("All of the fields must be filled in before creating an account"))

@st.dialog(tr("Delete account"))
def deleteAccount(accName, uid):
    st.write(f"{tr('Are you sure you want to delete')} {accName}?")
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button(tr("Yes")):
            firebase.deleteAccount(uid=uid)
            firebase.deleteData(uid=uid, id_token=userToken)
            st.rerun()
        elif st.button(tr("No"), type="primary"):
            st.rerun()
@st.dialog(tr("Reset Password"))
def resetAccountPassword(accEmail):
     st.write(f"{tr('Are you sure you want to reset')} {accEmail}?")
     with st.container(horizontal=True, vertical_alignment="center"):
             if st.button(tr("Yes")):
                 firebase.resetPassword(accEmail)
                 st.rerun()
             elif st.button(tr("No"), type="primary"):
                 st.rerun()

def accountCard(uid, account):
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(account["name"])
            st.write(account["email"])
            action = st.menu_button("", type="tertiary", icon=":material/more_vert:",options=[tr("Delete Account"), tr("Reset Password"), tr("Show QR")], key=f"menu{account["name"]}")
            if action == tr("Delete Account"):
                deleteAccount(account["name"], uid)
            if action == tr("Reset Password"):
                resetAccountPassword(account["email"])
            if action == tr("Show QR"):
                showqr(uid, account["name"])
        st.caption(uid)

accounts = fetchAccounts()

st.title(tr("Manage Accounts"))

with st.container(horizontal=True, vertical_alignment="center", width="content"):
    if st.button(tr("Create"), type='primary', icon=":material/add:"):
            createAccount()
    if st.button(tr("Upload"), type='primary', icon=":material/upload:"):
            accountbulkupload()

    if st.button(tr("Refresh"), type='secondary', icon=":material/refresh:"):
            accounts = fetchAccounts()

search_query = st.text_input(
    tr("Search accounts"),
    placeholder=tr("Search by name, email, or user ID"),
    icon=":material/search:",
).strip().casefold()

accounts = accounts or {}
coachTab, studentTab = st.tabs([tr("Coaches"), tr("Students/Parents")])

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