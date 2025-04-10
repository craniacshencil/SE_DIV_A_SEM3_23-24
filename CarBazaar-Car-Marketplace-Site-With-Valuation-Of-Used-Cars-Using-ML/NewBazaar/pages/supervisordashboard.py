import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from yaml.loader import SafeLoader
from streamlit_option_menu import option_menu
from pymongo import MongoClient
import requests
from io import BytesIO
from PIL import Image
import time

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

if (not authentication_status) or (name != "supervisor2"):
    switch_page("Login")

#Logout
colspace, colspace2, column1 = st.columns((8, 10, 2))

with column1:
    if st.session_state["authentication_status"]:
        authenticator.logout(f'{name} Logout', 'main', key='unique_key')

#Header image and text
st.columns(3)[1].image("images\\header.png",use_column_width="auto")

#Header Text
st.header("Supervisor Dashboard", divider = "red")
st.session_state['car_under_supervision'] = "No car"

#Initilazing mongoDb connection
client = MongoClient("localhost", 27017)
db = client.carbazaar
listings = db.post
appointments = db.appointment
cars = list(listings.find({"Inspectionstatus" : "Admin Approval Granted"}))

#Fetching the display images
display_images = []
display_images_urls = [car.get("Displayimage") for car in cars]
for url in display_images_urls:
    response = requests.get(url, stream = True)
    if response.status_code == 200:
        display_image = Image.open(BytesIO(response.content))
        display_images.append(display_image)

#Content
if len(cars) == 0:
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
    lmargin, col1, col2, col3, rmargin = st.columns([0.075, 0.25, 0.25, 0.25, 0.075])
    cols = [col1, col2, col3]
    i = 0
    for car in cars:
        appointment = appointments.find_one({"id_in_post" : car['_id']})
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
                    st.markdown(f"##### Date: {appointment['Inspection date']} · Time: {appointment['Inspection time']}")
                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    st.markdown(f"### ₹{carprice} Lakh")
                    st.write("")
                with col2:
                    st.write("")
                    inspect = st.button(label = "Start Inspection", key = button_key, use_container_width = True, type = "primary")
                    i = i + 1
                    if inspect:
                        filter = {'_id' : car['_id']}
                        update = { '$set' : {"Inspectionstatus" : "Inspection underway"}}
                        listings.update_one(filter, update)
                        st.session_state['car_under_supervision'] = car
                        st.toast("Redirecting to continue Inspection")
                        time.sleep(1)
                        switch_page('interiorfeatures')

