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
from streamlit_extras.colored_header import colored_header

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

#Session state for car to be checked further
st.session_state['Car_for_inspection'] = "No car"

#Initializing Mongo connection
client = MongoClient("localhost", 27017)
db = client.carbazaar
listings = db.post
cars = list(listings.find({"Seller" : name}))

#NavBar config
nav_bar = option_menu(None, ["Home", "Check Valuation", "Buy", "My Listings", "Wishlist", "Book Inspection"],
    icons=["house-fill", 'cash-coin', "car-front", "bag", "bookmark-heart-fill", "tools"],
    menu_icon="cast", default_index = 5, orientation="horizontal")
if nav_bar == "Home":
    switch_page("dashboard")
if nav_bar == "My Listings":
    switch_page("mylisting")
if nav_bar == "Check Valuation":
    switch_page("valuation")
if nav_bar == "Buy":
    switch_page("listings")
if nav_bar == "Wishlist":
    switch_page("wishlist")

#Content
st.header("Book Inspection", divider = "red")
with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(255, 255, 255, 1);
                    border-radius: 1rem;
                    padding: calc(2em - 2px)
                }
                """,
        ):
            col1, col2 = st.columns([0.98, 0.02])
            with col1:
                colored_header(label = "Benefits of having your car inspected: ", color_name = "red-70", description = "")
                st.write(" ")
                st.markdown("##### - Thorough Inspection: Your car will be comprehensively inspected by trained professionals \
                covering various aspects, including the engine, transmission, brakes, suspension and more")
                st.write(" ")
                st.markdown("##### - Quality Assurance: Approved cars are assured, thoroughly checked and do not have any major issues.")
                st.write("")

st.divider()

#Fetching the display images
display_images = []
display_images_urls = [car.get("Displayimage") for car in cars]
for url in display_images_urls:
    response = requests.get(url, stream = True)
    if response.status_code == 200:
        display_image = Image.open(BytesIO(response.content))
        display_images.append(display_image)

#Displaying the cars
if(len(cars) == 0):
    with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(255, 255, 255, 1);
                    border-radius: 1rem;
                    padding: calc(2em - 1px)
                }
                """,
        ):
            margin, col = st.columns([0.15, 0.85])
            with col:
                new_title = '<h3 style="font-family:sans-serif; color:Red; font-size: 30px;">ERROR: You have 0 listed cars. List a car, then book inspection.</h3>'
                st.markdown(new_title, unsafe_allow_html = True)

else:
    i = 0
    for car in cars:
            with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(255, 255, 255, 1);
                    border-radius: 1rem;
                    padding: calc(1em - 1px)
                }
                """,
            ):
                button_key = f"button_{i}"
                carbrand = car.get("Brand").capitalize()
                carmodel = car.get("Model").capitalize()
                carmyear = car.get("Myear")
                carfuel = car.get("Fueltype").capitalize()
                cartransmission = car.get("Transmission").capitalize()
                carvariant = car.get("Variant").capitalize()
                carkms = car.get("Kms")
                carprice = car.get("Priceinlakh")

                col1, col2, col3 = st.columns([3, 5, 2])
                
                with col1:
                    st.image(display_images[i])
                with col2:
                    margin, col = st.columns([0.1, 0.9])
                    with col:
                        st.header("")
                        st.header("")
                        st.markdown(f"### {carmyear} {carbrand} {carmodel} {carvariant}")
                        st.markdown(f"#### {carfuel} · {cartransmission} · {int(car['Kms'] / 1e3)}k kms")

                with col3:
                    st.title(" ")
                    st.title(" ")
                    st.write(" ")
                    check_status = st.button(label = "Check Inspection Status", key = button_key, type = "primary", use_container_width = True)
                    i = i + 1
                    if check_status:
                        st.session_state['Car_for_inspection'] = car
                        switch_page("inspectionstatus")
            st.divider()