import time
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from streamlit_option_menu import option_menu
import pymongo
from pymongo import MongoClient
import requests
from PIL import Image
from io import BytesIO
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authentication_status = st.session_state["authentication_status"]
name = st.session_state["name"]

if not authentication_status:
    switch_page("Login")

# Remove sidebar via CSS and adding header image
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

#Logout
colspace, colspace2, column1 = st.columns((0.1, 0.7, 0.2))

with column1:
    if st.session_state["authentication_status"]:
        authenticator.logout(f'{name} Logout', 'main', key='unique_key')
        
st.columns(3)[1].image("images\\header.png" ,use_column_width="auto")

#NavBar config
nav_bar = option_menu(None, ["Home", "Check Valuation", "Buy", "My Listings", "Wishlist", "Book Inspection"],
    icons=["house-fill", 'cash-coin', "car-front", "bag", "bookmark-heart-fill", "tools"],
    menu_icon="cast", default_index = 3, orientation="horizontal")
if nav_bar == "Home":
    switch_page("dashboard")
if nav_bar == "Wishlist":
    switch_page("wishlist")
if nav_bar == "Check Valuation":
    switch_page("valuation")
if nav_bar == "Buy":
    switch_page("listings")
if nav_bar == "Book Inspection":
    switch_page("bookinspection")

#Header text
st.header("My listings", divider = "red")

#Content
st.session_state['deletedcar'] = None
#MongoDB config
client = MongoClient("localhost", 27017)
db = client.carbazaar
listings = db.post
cars = list(listings.find({"Seller" : st.session_state['name']}))

#Fetching the display images
display_images = []
display_images_urls = [car.get("Displayimage") for car in cars]
for url in display_images_urls:
    response = requests.get(url, stream = True)
    if response.status_code == 200:
        display_image = Image.open(BytesIO(response.content))
        display_images.append(display_image)

#Container creation
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]
i = 0
for car in cars:
    button_key = f"button_{i}"
    button_key2 = f"button2_{i}"
    carbrand = car.get("Brand").capitalize()
    carmodel = car.get("Model").capitalize()
    carmyear = car.get("Myear")
    carfuel = car.get("Fueltype").capitalize()
    cartransmission = car.get("Transmission").capitalize()
    carvariant = car.get("Variant").capitalize()
    carkms = car.get("Kms")
    carprice = car.get("Priceinlakh")
    a = cols[i % 3]
    with a:
        with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(255, 255, 255, 1);
                    border-radius: 1rem;
                    padding: calc(0.75em - 1px)
                }
                """,
        ):
            col1, col2 = st.columns([0.999, 0.001])
            with col1:
                image = display_images[i]
                st.image(image, use_column_width = "always")
                st.markdown(f"#### {carmyear} {carbrand} {carmodel} {carvariant}")
                st.caption(f"{carfuel} · {cartransmission} · {int(car['Kms'] / 1e3)}k kms")
            col1, col2, col3, col4 = st.columns([0.35, 0.12, 0.15, 0.28], gap = "small")
            with col1:
                st.markdown(f"### ₹{carprice} Lakh")
                st.write("")
            with col2:
                st.empty()
                if(car['Inspectionstatus'] == "Inspection Successful"):
                    approved = '<h4 style="font-family:sans-serif; color:LightGreen;">(✅︎)</h4>'
                    st.markdown(approved, unsafe_allow_html = True)
            with col3:
                view = st.button(label = "View", key = button_key2, use_container_width = True, type = "primary")
                if view:
                    st.session_state['car'] = car
                    st.toast("Redirecting to your listing")
                    time.sleep(2)
                    switch_page('detailedlisting')
            with col4:
                cancel = st.button(label = "Delete Listing", key = button_key, use_container_width = True, type = "primary")
                st.session_state['deletedcar'] = car
                i = i + 1
                if cancel:
                    st.toast("Redirecting to delete listing....")
                    time.sleep(2)
                    switch_page('deletelisting')
                