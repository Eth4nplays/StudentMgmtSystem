import datetime

import requests
import streamlit as st
from firebase_admin import credentials, auth, db

# majority of these functions are based on the firebase rest api through requests
# - get docs from here: https://firebase.google.com/docs/reference/rest/
# only use the firebase admin sdk if needed (example deleting an account)
# - get docs from here: https://firebase.google.com/docs/reference/admin/python

API_KEY = st.secrets["firebase"]["api_key"]

def login(email, password):
    '''
    uses the rest api from firebase to authenticate user

    response payload (copied from docs):
    - idToken	string	A Firebase Auth ID token for the authenticated user.
    - email	string	The email for the authenticated user.
    - refreshToken	string	A Firebase Auth refresh token for the authenticated user.
    - expiresIn	string	The number of seconds in which the ID token expires.
    - localId	string	The uid of the authenticated user.
    - registered	boolean	Whether the email is for an existing account.
    '''
    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:signInWithPassword?key={API_KEY}"
    )

    response = requests.post(
        url,
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True,
        },
    )

    if response.ok:
        return response.json()

    return None

def createAccount(email, password):
    '''
    uses the rest api from firebase to authenticate user

    response payload (copied from docs):
    - idToken - A Firebase Auth ID token for the newly created user.
    - email - The email for the newly created user.
    - refreshToken - A Firebase Auth refresh token for the newly created user.
    - expiresIn - The number of seconds in which the ID token expires.
    - localId - The uid of the newly created user.
    '''
    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:signUp?key={API_KEY}"
    )

    response = requests.post(
        url,
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True,
        },
    )

    if response.ok:
        return response.json()

    return None

def resetPassword(email):
    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:sendOobCode?key={API_KEY}"
    )

    response = requests.post(
        url,
        json={
            "email": email,
            "requestType":"PASSWORD_RESET"
        },
    )

    if response.ok:
        return response.json()

    return None

def deleteAccount(uid):
    try:
        # Delete Authentication account
        auth.delete_user(uid)
        return True

    except Exception as e:
        return False

def getData(uid, id_token):
    '''
    checks firebase rtdb for the user role
    '''
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/users/{uid}.json"
        f"?auth={id_token}"
    )

    response = requests.get(url)
    if response.ok:
        return response.json()

    return None

def deleteData(uid, id_token):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/users/{uid}.json"
        f"?auth={id_token}"
    )

    response = requests.delete(url)
    if response.ok:
        return True

    return False

def getAccounts(id_token):
    '''
    gets all users from Firebase Realtime Database
    '''
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/users.json"
        f"?auth={id_token}"
    )

    response = requests.get(url)

    if response.ok:
        return response.json()

    return None

def setData(uid, id_token, role, name, email):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/users/{uid}.json"
        f"?auth={id_token}"
    )

    payload = {"role":role, "name":name, "email":email}
    response = requests.put(url, json=payload)
    if response.ok:
        return response.json()

    return None

def setLastReadAnnouncement(uid, id_token, date):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/users/{uid}.json"
        f"?auth={id_token}"
    )

    payload = {"lastread":date}
    response = requests.patch(url, json=payload)
    if response.ok:
        return response.json()

    return None

def setUserLanguage(uid, id_token, language):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/users/{uid}.json"
        f"?auth={id_token}"
    )

    response = requests.patch(url, json={"language": language})
    if response.ok:
        return response.json()

    return None

def setAnnouncement(id_token, roles, content, title, date):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/announcements/{date}.json"
        f"?auth={id_token}"
    )
    payload = {"title":title, "content":content, "roles":roles}
    response = requests.put(url, json=payload)
    if response.ok:
        return response.json()

    return response.json()

def deleteAnnouncement(title, id_token):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/announcements/{title}.json"
        f"?auth={id_token}"
    )

    response = requests.delete(url)
    if response.ok:
        return True

    return False


def getAnnouncement(id_token):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/announcements.json"
        f"?auth={id_token}"
    )

    response = requests.get(url)

    if response.ok:
        return response.json()

    return None

def createClass(id_token, classSchedule, classCode, className, classOwner):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}.json"
        f"?auth={id_token}"
    )
    payload = {"code":classCode, "classSchedule":classSchedule, "classOwner":classOwner}
    response = requests.put(url, json=payload)
    if response.ok:
        return response.json()

    return response.json()

def editClass(id_token, className, field, value):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}/{field}.json"
        f"?auth={id_token}"
    )

    response = requests.put(url, json=value)

    if response.ok:
        return response.json()

    response.raise_for_status()

def editAttendance(id_token, className, field, value):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}/attendance/{field}.json"
        f"?auth={id_token}"
    )

    response = requests.patch(url, json=value)

    if response.ok:
        return response.json()

    response.raise_for_status()

def getTask(id_token, className):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}/tasks.json"
        f"?auth={id_token}"
    )

    response = requests.get(url)

    if response.ok:
        return response.json()

    return None

def createTask(id_token, className, taskName, contents, totalGrade, deadline ):
    '''
    totalGrade can be either an integer or None. if it's none, it is an ungraded task.
    '''
    date=datetime.datetime.now().strftime("%y %m %d %H %M")
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}/tasks/{date}.json"
        f"?auth={id_token}"
    )

    payload = {"title":taskName, "contents":contents, "totalGrade":totalGrade, "deadline":deadline}

    response = requests.put(url, json=payload)

    if response.ok:
        return response.json()

    response.raise_for_status()

def deleteTask(id_token, className, date):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}/tasks/{date}.json"
        f"?auth={id_token}"
    )

    response = requests.delete(url)
    if response.ok:
        return True

    return False

def editTask(id_token, className, date, taskName, contents, totalGrade, deadline):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}/tasks/{date}.json"
        f"?auth={id_token}"
    )
    payload = {"title":taskName, "contents":contents, "totalGrade":totalGrade, "deadline":deadline}

    response = requests.patch(url, json=payload)

    if response.ok:
        return response.json()

    response.raise_for_status()

def submitTask(id_token, name, className, date, submissionContent):
    '''
    name is the username of the student who submitted it.
    submissionContent is what they submit.
    '''
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}/tasks/{date}/submissions/{name}.json"
        f"?auth={id_token}"
    )
    
    payload = {"submission":submissionContent}
    
    deadline = requests.get(f"{st.secrets['firebase']['database_url']}"
                            f"/classes/{className}/tasks/{date}.json"
                            f"?auth={id_token}"
                        ).json()["deadline"] 
    
    if datetime.datetime.now() <= datetime.datetime.strptime(deadline, "%y %m %d %H %M"):
        response = requests.put(url, json=payload)
        if response.ok:
            return response.json()
        response.raise_for_status()
    return False

def unsubmitTask(id_token, name, className, date):
    '''
    name is the username of the student who submitted it.
    submissionContent is what they submit.
    '''
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}/tasks/{date}/submissions/{name}.json"
        f"?auth={id_token}"
    )
    deadline = requests.get(f"{st.secrets['firebase']['database_url']}"
                            f"/classes/{className}/tasks/{date}.json"
                            f"?auth={id_token}"
                        ).json()["deadline"] 
    
    if datetime.datetime.now() <= datetime.datetime.strptime(deadline, "%y %m %d %H %M"):
        response = requests.delete(url)
        if response.ok:
            return True
        response.raise_for_status()
    else:
        return False

def gradeTask(id_token, studentName, className, date, grade, comment):
    '''
    for teachers to grade the task.
    '''
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}/tasks/{date}/submissions/{studentName}.json"
        f"?auth={id_token}"
    )

    payload = {"grade":grade, "comment":comment}

    response = requests.patch(url, json=payload)

    if response.ok:
        return response.json()

    response.raise_for_status()

def joinClass(id_token, classCode, studentUID):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes.json"
        f"?auth={id_token}"
    )
    response = requests.get(url)
    if response.ok:
        classes = response.json()
        for className, classData in classes.items():
            if classData["code"] == classCode:
                # add studentUID to the class's students list
                if "students" not in classData:
                    classData["students"] = []
                classData["students"].append(f"{studentUID} {getData(studentUID, id_token)["name"]}")
                # update the class data
                update_url = (
                    f"{st.secrets['firebase']['database_url']}"
                    f"/classes/{className}.json"
                    f"?auth={id_token}"
                )
                update_response = requests.put(update_url, json=classData)
                if update_response.ok:
                    return True

    return False

def getClass(id_token, className):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}.json"
        f"?auth={id_token}"
    )

    response = requests.get(url)

    if response.ok:
        return response.json()

    return None

def getClassReports(id_token, className):
    
    class_data = getClass(id_token, className)
    if class_data is None:
        return None

    tasks = class_data.get("tasks") or {}
    students = set(class_data.get("students") or [])
    for task in tasks.values():
        students.update((task.get("submissions") or {}).keys())

    grades = {
        student: {
            task_id: {
                "title": task.get("title", task_id),
                "grade": "Not submitted",
                "totalGrade": task.get("totalGrade"),
            }
            for task_id, task in tasks.items()
        }
        for student in students
    }

    for task_id, task in tasks.items():
        for student, submission in (task.get("submissions") or {}).items():
            grades[student][task_id]["grade"] = submission.get("grade")

    return grades

def getClasses(id_token):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes.json"
        f"?auth={id_token}"
    )

    response = requests.get(url)

    if response.ok:
        return response.json()

    return None

def deleteClass(id_token, className):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}.json"
        f"?auth={id_token}"
    )

    response = requests.delete(url)
    if response.ok:
        return True

    return False

def leaveClass(id_token, className, uid):
    # Get the class data
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/classes/{className}.json"
        f"?auth={id_token}"
    )
    
    response = requests.get(url)
    if response.ok:
        classData = response.json()
        # Remove student from the students array
        if "students" in classData and f"{uid} {getData(uid, id_token)["name"]}" in classData["students"]:
            classData["students"].remove(f"{uid} {getData(uid, id_token)["name"]}")
            # Update the class data
            update_response = requests.put(url, json=classData)
            if update_response.ok:
                return True
    
    return False

def getRooms(id_token):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/rooms.json"
        f"?auth={id_token}"
    )

    response = requests.get(url)

    if response.ok:
        return response.json() or {}

    return None

def getRoomBookings(id_token, date):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/rooms.json"
        f"?auth={id_token}"
    )

    response = requests.get(url)

    if response.ok:
        rooms = response.json() or {}
        bookings = {}
        for roomName, roomData in rooms.items():
            date_bookings = (roomData or {}).get(date) or {}
            if "coach" in date_bookings:
                date_bookings = [date_bookings]
            else:
                date_bookings = list(date_bookings.values())
            bookings[roomName] = date_bookings
        return bookings

    return None

def createRoom(id_token, roomName):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/rooms/{roomName}.json"
        f"?auth={id_token}"
    )

    response = requests.put(url, json={"name":roomName})
    if response.ok:
        return True

    response.raise_for_status()


def bookRoom(id_token, roomName, date, startTime, endTime, coachName, className):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/rooms/{roomName}/{date}.json"
        f"?auth={id_token}"
    )

    check_response = requests.get(url)
    if not check_response.ok:
        check_response.raise_for_status()
    bookings = check_response.json() or {}
    if "coach" in bookings:
        return False

    start = datetime.datetime.strptime(startTime, "%H:%M").time()
    end = datetime.datetime.strptime(endTime, "%H:%M").time()
    if start >= end:
        return False

    for booking in bookings.values():
        existing_start = booking.get("start")
        existing_end = booking.get("end")
        if not existing_start or not existing_end:
            return False
        if startTime < existing_end and endTime > existing_start:
            return False

    payload = {
        "start": startTime,
        "end": endTime,
        "coach": coachName,
        "class": className
    }
    bookingKey = startTime.replace(":", "-")
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/rooms/{roomName}/{date}/{bookingKey}.json"
        f"?auth={id_token}"
    )
    response = requests.put(url, json=payload)

    if response.ok:
        return True

    response.raise_for_status()