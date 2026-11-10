from datetime import datetime

import cv2
import numpy as np
import streamlit as st

from helpers import cookies, firebase
from helpers.localization import normalize_language, translate

language = normalize_language(st.session_state["profile"].get("language"))
tr = lambda text: translate(text, language)

st.header(tr("Attendance Scanner"))
st.write(f"{tr('Scan your QR code for your attendance on')} {st.session_state['selected_class']}")
image = st.camera_input(" ")

if cookies.getCookies("token") != None:
        userToken = cookies.getCookies("token")
else:
    userToken = st.session_state['token']

if image is not None:
    bytes_data = image.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    detector = cv2.QRCodeDetector()

    data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

    if data:
        uid, name = data.split(" ", 1)
        date_str = datetime.now().strftime("%d-%m-%Y")

        result = firebase.editAttendance(
                    id_token=userToken,
                    className=st.session_state["selected_class"],
                    field=date_str,
                    value={name: True}
                )
        
        if result:
            st.success(f"{tr('Attendance recorded for')} {name} {tr('on')} {date_str}.")
        else:
            st.error(tr("Failed to submit attendance. Please try again."))