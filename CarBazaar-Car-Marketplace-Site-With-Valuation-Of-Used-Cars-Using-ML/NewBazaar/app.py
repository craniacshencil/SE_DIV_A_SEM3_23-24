import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
import base64
from st_clickable_images import clickable_images
import os
# Collapse sidebar on start, remove it and header image
st.set_page_config(initial_sidebar_state="collapsed",layout="wide")
st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)
st.columns(3)[1].image("images/header.png",use_column_width="auto")

#Checking for temp_storage folder
try:
    os.mkdir("temp_storage")
except OSError as error: 
    print("[IGNORE] File already exists")

#Adding NavBar
nav_bar = option_menu(None, ["Home", "Login", "Register"],
    icons=['house', 'cloud-upload', "list-task"],
    menu_icon="cast", default_index=0, orientation="horizontal")

if nav_bar == "Login":
	switch_page("login")

if nav_bar == "Register":
	switch_page("register")
	
#Content
# col1, col2 = st.columns(2,gap="small")
# with col1:
# 	st.image("images/buy_now.png")
# with col2:
# 	st.image("images/sell_ride.png")

col1, col2 = st.columns([0.05, 0.95])
with col2:
    images = []
    for file in ["images//buy_now.png", "images//sell_ride.png"]:
        with open(file, "rb") as image:
            encoded = base64.b64encode(image.read()).decode()
            images.append(f"data:image/jpeg;base64,{encoded}")

    clicked = clickable_images(
        images,
        titles = ["buy", "sell"],
        div_style = {"display": "block", "justify-content": "flex-start", "flex-wrap": "nowrap", "width" : "1200px"},
        img_style = {"margin": "1px", "height": "590px", "width" : "590px"},
    )

    if clicked == 0:
          switch_page("listings")
    if clicked == 1:
          switch_page("valuation")
