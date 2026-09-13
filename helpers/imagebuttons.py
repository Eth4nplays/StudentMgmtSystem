import base64
import streamlit as st

def encodeImage(image):
    with open(image, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
        return f"data:image/jpeg;base64,{encoded}"

def imageButtons(page, image, width, height):
    st.markdown(f"""
    <style>
    a[data-testid="stPageLink-NavLink"][href*="{page.split("/")[-1].removesuffix(".py")}"] {{
        width: {width/5}px;
        height: {height/5}px;
        background: url("{encodeImage(image)}") center/contain no-repeat;
    }}
    </style>
    """, unsafe_allow_html=True)
    st.page_link(page, label=" ")

def image(image, width):
    st.markdown(
        f'<img src="{encodeImage(image)}" '
        f'style="width:{width}px; object-fit:contain;">',
        unsafe_allow_html=True
    )