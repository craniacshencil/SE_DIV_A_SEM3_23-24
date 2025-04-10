import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from yaml.loader import SafeLoader
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
from PIL import Image
from io import BytesIO
from streamlit_extras.stylable_container import stylable_container

#Check Login status
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
    menu_icon="cast", default_index = 4, orientation="horizontal")
if nav_bar == "Home":
    switch_page("dashboard")
if nav_bar == "My Listings":
    switch_page("mylisting")
if nav_bar == "Check Valuation":
    switch_page("valuation")
if nav_bar == "Buy":
    switch_page("listings")
if nav_bar == "Book Inspection":
    switch_page("bookinspection")

#MongoDB init and logic
cars = []
client = MongoClient("localhost", 27017)
db = client.carbazaar
wishlist_coll = db.wishlist
post_coll = db.post

users_wishlist = list(wishlist_coll.find({"User" : st.session_state['name']}))
wishlisted_ids = [item.get('id_in_post') for item in users_wishlist]

for id in wishlisted_ids:
    car = post_coll.find_one({'_id' : id})
    cars.append(car)

#Content
st.header("Wishlist", divider = "red")

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
                st.image(display_images[i], use_column_width = "always")
                st.markdown(f"#### {carmyear} {carbrand} {carmodel} {carvariant}")
                st.caption(f"{carfuel} · {cartransmission} · {int(car['Kms'] / 1e3)}k kms · by {car['Seller']}")
            col1, col2, col3 = st.columns([0.44, 0.36, 0.2])
            with col1:
                st.markdown(f"### ₹{carprice} Lakh")
                st.write("")
            with col2:
                st.caption("")
                if(car['Inspectionstatus'] == "Inspection Successful"):
                    approved = '<h5 style="font-family:sans-serif; color:LightGreen;">(Approved✓)</h5>'
                    st.markdown(approved, unsafe_allow_html = True)
            with col3:
                view = st.button(label = "View", key = button_key, use_container_width = True, type = "primary")
                i = i + 1
                if view:
                    st.session_state['car'] = car
                    switch_page('detailedlisting')

