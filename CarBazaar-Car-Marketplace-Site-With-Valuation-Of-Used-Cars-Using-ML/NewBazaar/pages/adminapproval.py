import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
from yaml.loader import SafeLoader
from streamlit_option_menu import option_menu
from pymongo import MongoClient
import requests
from PIL import Image
from io import BytesIO

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

#Check Login Status
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

if (not authentication_status) or (name != "admin2"):
    switch_page("Login")

#Logout
colspace, colspace2, column1 = st.columns((8, 10, 2))

with column1:
    if st.session_state["authentication_status"]:
        authenticator.logout(f'{name} Logout', 'main', key='unique_key')

#Header image and text
st.columns(3)[1].image("images\\header.png",use_column_width="auto")

#Nav-bar
nav_bar = option_menu(None, ["Inspection Approval", "Ban Users"],
    icons=["tools", "exclamation-diamond"],
    menu_icon="cast", default_index = 0, orientation="horizontal")
if nav_bar == "Ban Users":
    switch_page("banuser")

#Header text
st.header("Admin Approval", divider = "red")

#Initilazing mongoDb connection
client = MongoClient("localhost", 27017)
db = client.carbazaar
listings = db.post
appointments = db.appointment
cars = list(listings.find({"Inspectionstatus" : "Applied for Inspection"}))

#Fetching the display images
display_images = []
display_images_urls = [car.get("Displayimage") for car in cars]
for url in display_images_urls:
    response = requests.get(url, stream = True)
    if response.status_code == 200:
        display_image = Image.open(BytesIO(response.content))
        display_images.append(display_image)

#Content
st.header("")
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
            margin, col = st.columns([0.27, 0.73])
            with col:
                new_title = "You are up-to date with all your work"
                st.markdown(f"## {new_title}")
                st.write("")

else:
    i = 0
    for car in cars:            
            approval_request = appointments.find_one({"id_in_post" : car.get("_id")})
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

                date = approval_request.get("Inspection date")
                time_ = approval_request.get("Inspection time")

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
                    st.title("")
                    st.write("")
                    st.markdown("##### Inspection date: " + date)
                    st.markdown("##### Inspection time: " + time_)
                    verdict = st.radio(label = "", options = ['Approve', 'Disapprove'], horizontal = True)
                    confirm = st.button("Confirm", use_container_width = True, type = "primary")
                    if confirm:
                        if verdict == 'Approve':
                            filter = {'_id' : car.get('_id')}
                            update = {'$set' : {"Inspectionstatus" : "Admin Approval Granted"}}
                            listings.update_one(filter, update)
                            st.toast("Admin Approval Granted!")
                        
                        if verdict == 'Disapprove':
                            filter = {'_id' : car.get('_id')}
                            update = {'$set' : {"Inspectionstatus" : "Admin Approval Denied"}}
                            listings.update_one(filter, update)
                            appointments.delete_one({"id_in_post" : car['_id']})
                            st.toast("Admin approval Denied")   
            st.divider()