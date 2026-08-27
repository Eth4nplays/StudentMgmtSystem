import requests
import streamlit as st

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

def setData(uid, id_token, role):
    url = (
        f"{st.secrets['firebase']['database_url']}"
        f"/users/{uid}.json"
        f"?auth={id_token}"
    )

    payload = {"role":role}
    response = requests.put(url, json=payload)
    if response.ok:
        return response.json()

    return None