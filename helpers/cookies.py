import streamlit as st
import extra_streamlit_components as stx
import datetime
cookie_manager = stx.CookieManager()


def batchCookies(cookieData):
    return cookie_manager.batch_set(cookieData, expires_at=datetime.datetime.now() + datetime.timedelta(days=365))

def setCookies(cookie, data, key):
    return cookie_manager.set(cookie, data, key=key, expires_at=datetime.datetime.now() + datetime.timedelta(days=365))

def getCookies(cookie):
    return cookie_manager.get(cookie)

@st.dialog("Logged out", dismissible=False)
def logout():
    st.write("Please refesh your browser.")
    cookies = ["uid", "token", "refreshToken"]

    for i in cookies:
        try:
            cookie_manager.delete(i, f"delete{i}")
        except Exception as e:
            st.error(f"Failed to delete {i}: {e}")
    return True