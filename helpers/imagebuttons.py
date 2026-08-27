import base64
import streamlit as st

def encodeImage(image):
    with open(image, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
        return f"data:image/jpeg;base64,{encoded}"

def imageButtons(page, image):
    st.markdown(f"""
    <style>
    a[data-testid="stPageLink-NavLink"] {{
        position: relative;
        width: 411.5px;
        height: 79px;
        font-size: 0; 
    }}
    a[data-testid="stPageLink-NavLink"]::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: url("{encodeImage(image)}") center/contain no-repeat;
    }}
    </style>
    """, unsafe_allow_html=True)
    st.page_link(page, label=" ")
