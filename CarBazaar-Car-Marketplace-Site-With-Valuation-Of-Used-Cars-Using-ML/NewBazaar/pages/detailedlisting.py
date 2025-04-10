#library imports
import streamlit as st
import numpy as np
import pandas as pd
import time
from PIL import Image
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_carousel import carousel
from streamlit_extras.stylable_container import stylable_container 
from streamlit_extras.grid import grid
import pymongo
from pymongo import MongoClient
import glob
import os
import shutil
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from bson.objectid import ObjectId


#Collapsing and removing sidebar, adding header image
st.set_page_config(initial_sidebar_state = "collapsed", layout = "wide")
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

# Remove sidebar,adding header image
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
image = Image.open("images\\header.png")
st.columns(3)[1].image(image)
colored_header(
label = "Selected Listing: ",
description = " ",
color_name = "red-70",
)

#Bringing in the required car
car = st.session_state['car']
phonenumber = st.session_state['phonenumber']

#Generating carousel out of urls
col1, col2 = st.columns([2, 1], gap = "small")
with col1:
    image_urls = car['Images']
    img_collection = []
    for url in image_urls:
        item = dict(title = "",
                    text = "",
                    interval = None,
                    img = url)
        img_collection.append(item)
    carousel(items = img_collection, width = 1)

#Car Overview
with col2:
    with stylable_container(
        key="container_with_border",
        css_styles="""
            {
                border: 2px solid rgba(60, 60, 60, 1);
                border-radius: 1rem;
                padding: calc(1em - 1px)
            }
            """,
    ):

        st.markdown(f"##### {car['Myear']} {car['Brand'].capitalize()} {car['Model'].capitalize()} {car['Variant'].capitalize()}")
        st.markdown(f"###### {int(car['Kms'] / 1e3)}k kms · {car['Fueltype'].capitalize()} · {car['Transmission']} · {car['Ownerno']} owner · by {car['Seller']}")
        col1, col2, col3 = st.columns([1, 40, 1])
        with col2:
            st.divider()
        col1, col2 = st.columns([1, 3])
        with col2:
            st.markdown(f"####  Price: ₹{car['Priceinlakh']} Lakh")
        col1, col2, col3 = st.columns([1, 40, 1])
        with col2:
            st.divider()
        col0, col1, col2 = st.columns([2, 3, 3])
        with col0:
            wishlist = st.button("Wishlist", use_container_width = True)
        with col2:
            emi = st.button("Calculate EMI", use_container_width = True)
        with col1:
            st.link_button("Contact Seller", f"https://wa.me/{car['Phonenumber']}", type = "primary", use_container_width = True)

#Wishlisting the car
if(wishlist):
    client = MongoClient("localhost", 27017)
    db = client.carbazaar
    wishlist_collection = db.wishlist
    wishlist_entries = list(db.wishlist.find({"User" : name}))
    wishlist_doc = {
        "User" : st.session_state['name'],
        "id_in_post" : car['_id']
    }
    post_ids = [entry.get('id_in_post') for entry in wishlist_entries]
    flag = 1
    for i in range(0, len(post_ids)):
        if car['_id'] == post_ids[i]:
            st.toast("Already wishlisted.")
            flag = 0
            break
    if flag == 1:
        st.toast("Wishlisted Sucessfully")
        wishlist_collection.insert_one(wishlist_doc)

#Switching to the loan page
if(emi):
    switch_page("loanbuyer")

#Displaying Basic details of the car
valve_config = car['Valveconfiguration']
kerb_wt = car['Kerbweight']
seats = car['Seats']
max_torque = car['Maxtorque']
body = car['Body']
gearbox = car['Gearbox']
steering_type = car['Steeringtype']
F_brake = car['Frontbrake']
R_brake = car['Rearbrake']
tyres = car['Tyres']
Fuelsupplysystem = car['Fuelsupplysystem']
tread = car['Tread']

st.divider()
with stylable_container(
    key="container_with_border",
    css_styles="""
        {
            border: 2px solid rgba(60, 60, 60, 1);
            border-radius: 1rem;
            padding: calc(1em - 1px)
        }
        """,
):
    st.subheader("General Features")
    my_grid = grid(4, vertical_align="bottom")
    # Row 1:
    my_grid.text_input(label = "Body", value = body.capitalize(), disabled = True)
    my_grid.text_input(label = "GearBox", value = gearbox, disabled = True)
    my_grid.text_input(label = "Seats", value = seats, disabled = True)
    my_grid.text_input(label = "Max Torque", value = f"{int(max_torque)} Nm", disabled = True)
    # Row 2:
    my_grid.text_input(label = "Fuel-Supply System", value = Fuelsupplysystem, disabled = True)
    my_grid.text_input(label = "Tyres", value = tyres.capitalize(), disabled = True)
    my_grid.text_input(label = "Steering Type", value = steering_type.capitalize(), disabled = True)
    my_grid.text_input(label = "Front Brake", value = F_brake.capitalize(), disabled = True)
    # Row 3:
    my_grid.text_input(label = "Rear Brake", value = R_brake.capitalize(), disabled = True)
    my_grid.text_input(label = "Tread", value = f"{str(int(tread))}", disabled = True)
    my_grid.text_input(label = "Valve Configuration", value = valve_config, disabled = True)
    my_grid.text_input(label = "Kerb Weight", value = f"{str(int(kerb_wt))}", disabled = True)

if len(car.keys()) > 27:
    interiorfeatures = car['Interiorfeatures']
    exteriorfeatures = car['Exteriorfeatures']
    comfortfeatures = car['Comfortfeatures']
    safetyfeatures = car['Safetyfeatures']

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    local_css("styles.css")

    with st.expander("Interior Features"):
        st.header("")
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        for i, feat in enumerate(interiorfeatures):
            with cols[i % 3]:
                st.markdown(f"##### · {feat}")
    with st.expander("Exterior Features"):
            st.header("")
            col1, col2, col3 = st.columns(3)
            cols = [col1, col2, col3]
            for i, feat in enumerate(exteriorfeatures):
                with cols[i % 3]:
                    st.markdown(f"##### · {feat}")
    with st.expander("Comfort Features"):
            st.header("")
            col1, col2, col3 = st.columns(3)
            cols = [col1, col2, col3]
            for i, feat in enumerate(comfortfeatures):
                with cols[i % 3]:
                    st.markdown(f"##### · {feat}")
    with st.expander("Safety Features"):
            st.header("")
            col1, col2, col3 = st.columns(3)
            cols = [col1, col2, col3]
            for i, feat in enumerate(safetyfeatures):
                with cols[i % 3]:
                    st.markdown(f"##### · {feat}")

#Go Back to the listings page
back = st.columns(5)[2].button("Back to listings")
if(back):
    switch_page("listings")