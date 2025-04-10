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
import requests 
from io import BytesIO


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
image = image.resize((300, int(300 * image.height / image.width)))
st.columns(3)[1].image(image)
colored_header(
label = "Confirm Listing: ",
description = " ",
color_name = "red-70",
)


#Empty out the entire folder containing uploaded images from imguplaod.py
for filename in os.listdir("temp_storage"):
    filepath = os.path.join("temp_storage", filename)
    try:
        shutil.rmtree(filepath)
    except OSError:
        os.remove(filepath)

#Generating carousel out of urls
col1, col2 = st.columns([2, 1], gap = "small")
with col1:
    image_urls = st.session_state['imageurls']
    img_collection = []
    for url in image_urls:
        item = dict(title = "",
                    text = "",
                    interval = None,
                    img = url)
        img_collection.append(item)
    carousel(items = img_collection, width = 1)

#Converting values back to original form for display
price = st.session_state['Price']
values = st.session_state['values']
name = st.session_state['name']
phonenumber = st.session_state['phonenumber']
display_image = st.session_state['Display_image']

if values[5] == 0:
    values[5] = "Manual"
else:
    values[5] = "Automatic"

if values[4] == 0:
    values[4] = "LPG"
if values[4] == 1:
    values[4] = "CNG"
if values[4] == 2:
    values[4] = "Petrol"
if values[4] == 3:
    values[4] = "Diesel"
if values[4] == 4:
    values[4] = "Electric"

if values[6] == 1:
    values[6] = "1st"
if values[6] == 2:
    values[6] = "2nd"
if values[6] == 3:
    values[6] = "3rd"
if values[6] == 4:
    values[6] = "4th"
if values[6] == 5:
    values[6] = "5th"
if values[6] == 6:
    values[6] = "6th"

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

        st.markdown(f"##### {values[1]} {values[0].capitalize()} {values[2].capitalize()} {values[3]}")
        st.markdown(f"###### {int(values[7] / 1e3)}k kms · {values[4]} · {values[5]} · {values[6]} owner · by {name}")
        col1, col2, col3 = st.columns([1, 40, 1])
        with col2:
            st.divider()
        col1, col2 = st.columns([1, 3])
        with col2:
            st.markdown(f"####  Price: ₹{price} Lakh")
            # st.caption("(Fixed On-road price)")
        col1, col2, col3 = st.columns([1, 40, 1])
        with col2:
            st.divider()
        col0, col1, col2 = st.columns([2, 3, 3], gap = "small")
        with col0:
            wishlist = st.button("Wishlist", use_container_width = True)
        with col2:
            emi = st.button("Calculate EMI", use_container_width = True)
        with col1:
            st.link_button("Contact Seller", f"https://wa.me/{phonenumber}", type = "primary", use_container_width = True)
if(wishlist):
	st.toast("Added to wishlist")
if(emi):
    switch_page("loanpreview")
#  values = [brand, yr, model, variant, fueltype
#          , transmission, owner, kms]

#Displaying Basic details of the car
df = pd.read_csv("data\\data_entry_train.csv")
df = df.loc[(df.model == values[2]) & (df.variant == values[3])]

valve_config = df['Valve Configuration'].mode()[0]
kerb_wt = df['Kerb Weight'].mode()[0]
seats = df['Seats'].mode()[0]
max_torque = df['Max Torque Delivered'].mode()[0]
body = df['body'].mode()[0]
gearbox = df['Gear Box'].mode()[0]
steering_type = df['Steering Type'].mode()[0]
F_brake = df['Front Brake Type'].mode()[0]
R_brake = df['Rear Brake Type'].mode()[0]
tyres = df['Tyre Type'].mode()[0]
Fuelsupplysystem = df['Fuel Supply System'].mode()[0]
tread = df['Tread'].mode()[0]

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

#Go Back to Dashboard and adding the listing to Database
finish = st.columns(5)[2].button("Confirm listing")
if(finish):
    client = MongoClient("localhost", 27017)
    db = client.carbazaar

    #  values = [brand, yr, model, variant, fueltype
    #          , transmission, owner, kms]
    post = {
        "Seller" : name,
        "Phonenumber" : phonenumber,
        "Priceinlakh" : price,
        "Images" : image_urls,
        "Displayimage" : display_image,
        "Inspectionstatus" : "Not Inspected",
        "Brand" : values[0], 
        "Myear" : int(values[1]), 
        "Model" : values[2],
        "Variant" : values[3],
        "Fueltype" : values[4],
        "Transmission" : values[5],
        "Ownerno" : values[6],
        "Kms" : values[7],
        "Valveconfiguration" : valve_config,
        "Kerbweight" : int(kerb_wt),
        "Seats" : int(seats),
        "Maxtorque" : int(max_torque),
        "Body" : body,
        "Gearbox" : gearbox,
        "Steeringtype" : steering_type,
        "Frontbrake" : F_brake,
        "Rearbrake" : R_brake,
        "Tyres" : tyres,
        "Fuelsupplysystem" : Fuelsupplysystem,
        "Tread" : int(tread)
    }

    listings = db.post
    listings.insert_one(post)
    st.success("Your Car has been successfully listed")
    st.toast("Redirecting to dashboard in 3 sec..")
    time.sleep(3)
    switch_page("dashboard")