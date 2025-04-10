import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from yaml.loader import SafeLoader
import pymongo
from pymongo import MongoClient
import requests
from PIL import Image
from io import BytesIO
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.colored_header import colored_header
import time
import datetime

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

#Session states
car = st.session_state['Car_for_inspection']

#DB variables, and their placeholders
inspection_date = ""
inspection_time = ""

#Connecting to DB
client = MongoClient("localhost", 27017)
db = client.carbazaar
appointments = db.appointment
listings = db.post

#Content
st.header("Inspection Status: ", divider= "red")
st.header("")

#Fetching the display image
url = car.get("Displayimage")
response = requests.get(url, stream = True)
if response.status_code == 200:
    display_image = Image.open(BytesIO(response.content))

#Displaying the car
carbrand = car.get("Brand").capitalize()
carmodel = car.get("Model").capitalize()
carmyear = car.get("Myear")
carfuel = car.get("Fueltype").capitalize()
cartransmission = car.get("Transmission").capitalize()
carvariant = car.get("Variant").capitalize()
carkms = car.get("Kms")
carprice = car.get("Priceinlakh")
carinspection = car.get("Inspectionstatus")
col1, column2 = st.columns([0.3, 0.7], gap = "large")
with col1:
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
            st.image(display_image, use_column_width = "always")
            st.markdown(f"#### {carmyear} {carbrand} {carmodel} {carvariant}")
            st.write("")
            st.caption(f"{carfuel} · {cartransmission} · {int(car['Kms'] / 1e3)}k kms · by {car['Seller']}")
            st.write("")
            st.markdown(f"## ₹{carprice} Lakh")
            st.subheader("")


with column2:
    colored_header(label = "Inspection Timeline", description = "", color_name = "red-70")
    st.header("")
    col1, col2, col3, col4, col5 = st.columns([.15,.18,.2,.2,.15])
    with col1:
        st.write("Not Inspected")
    with col2:
        st.write("Applied for Inspection")
    with col3:
        st.write("Admin Approval Granted")
    with col4:
        st.write("Inspection underway")
    with col5:
        st.write("Inspection Successful")
    
    inspection_status_bar = st.progress(0, text = " ")
    
    if carinspection == "Not Inspected":
        progress = 5
        st.error("Your car has not been inspected.")
        st.divider()
        st.markdown("##### When do you want your car to be inspected?")
        datecol, timecol = st.columns(2)
        with datecol:
            date = st.date_input(label = "Choose date", min_value = datetime.datetime.now(), format = "DD/MM/YYYY")
        with timecol:    
            time_ = st.time_input(label = "Choose time", step = 1800)

        confirm = st.columns(3)[1].button("Confirm", use_container_width = True)
        if confirm:
            date = date.strftime("%d/%m/%Y")
            time_ = time_.strftime("%H:%M")
            ####MongoCode#####
            appointment = {
                "User" : name,
                "id_in_post" : car['_id'],
                "Inspection date" : date,
                "Inspection time" : time_
            }
            appointments.insert_one(appointment)
            update = {"$set": {"Inspectionstatus": "Applied for Inspection"}}
            filter = {"_id" : car['_id']}
            listings.update_one(filter, update)

            st.toast("We have recorded your booking")
            time.sleep(1)
            st.toast("Redirecting to dashboard in 3 seconds")
            time.sleep(3)
            switch_page("dashboard")

    if carinspection == "Applied for Inspection":
        progress = 25
        st.info("Your application is being processed.")

    if carinspection == "Admin Approval Granted":
        progress = 46
        st.info("Your car has been approved by admin and is sent for inspection.")
        #######MongoCode#########
        car_for_admin_approval = appointments.find_one({"id_in_post" : car['_id']})
        inspection_date = car_for_admin_approval.get("Inspection date")
        inspection_time = car_for_admin_approval.get("Inspection time")
        st.write("")
        lmargin, textcol = st.columns([0.12, 0.88])
        with textcol:
            st.subheader(f"Confirmed!! Your inspection is on {inspection_date} at {inspection_time}")
    
    if carinspection == "Admin Approval Denied":
        progress = 5
        st.error("Admin has denied your booking for inspection")
        st.info("Possibly because of: Overpacked warehouses, fully booked timeslots etc.")
        car_denied_by_admin = appointments.find_one({'id_in_post' : car['_id']})
        st.divider()
        st.markdown("##### Book another inspection?")
        datecol, timecol = st.columns(2)
        with datecol:
            date = st.date_input(label = "Choose date", min_value = datetime.datetime.now(), format = "DD/MM/YYYY")
        with timecol:    
            time_ = st.time_input(label = "Choose time", step = 1800)
        confirm = st.columns(3)[1].button("Confirm", use_container_width = True)
        if confirm:
            date = date.strftime("%d/%m/%Y")
            time_ = time_.strftime("%H:%M")
            ####MongoCode#####
            appointment = {
                "User" : name,
                "id_in_post" : car['_id'],
                "Inspection date" : date,
                "Inspection time" : time_
            }
            appointments.insert_one(appointment)
            update = {"$set": {"Inspectionstatus": "Applied for Inspection"}}
            filter = {"_id" : car['_id']}
            listings.update_one(filter, update)
            st.toast("We have recorded your booking")
            time.sleep(1)
            st.toast("Redirecting to dashboard in 3 seconds")
            time.sleep(3)
            switch_page("dashboard")


    if carinspection == "Inspection underway":
        progress = 69
        st.info("Our Supervisors are currently inspecting your car")

    if carinspection == "Inspection Successful":
        progress = 100
        st.success("Our Supervisors have completed the inspection.")
        st.info("Check out your listing!!")
        st.header("")
        to_listing = st.columns(3)[1].button("Go to my listings", use_container_width = True, type = "primary")
        if to_listing:
            st.toast("Redirecting to your listings...")
            time.sleep(2)
            switch_page("mylisting")

    
    for percent_complete in range(progress):
        time.sleep(0.0001)
        inspection_status_bar.progress(percent_complete + 1, text = " ")
st.divider()
back = st.columns(3)[1].button("Back", use_container_width = True)
if back:
    switch_page("bookinspection")
