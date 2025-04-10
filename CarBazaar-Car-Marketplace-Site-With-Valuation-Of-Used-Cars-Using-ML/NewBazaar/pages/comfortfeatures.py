from pymongo import MongoClient
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
from yaml.loader import SafeLoader
from streamlit_option_menu import option_menu
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
st.header("Comfort features <3/5>", divider = "red")
st.header("")
car = st.session_state['car_under_supervision']
st.session_state['comfort_features'] = "Not set"
carinfo = st.session_state['carinfo']

#Content
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
    carbrand = car.get("Brand").capitalize()
    carmodel = car.get("Model").capitalize()
    carmyear = car.get("Myear")
    carfuel = car.get("Fueltype").capitalize()
    cartransmission = car.get("Transmission").capitalize()
    carvariant = car.get("Variant").capitalize()
    carkms = car.get("Kms")
    carprice = car.get("Priceinlakh")

    col1, col2, col3 = st.columns([3, 5, 3])
    with col1:
        st.image(carinfo['Display image'])
    with col2:
        margin, col = st.columns([0.1, 0.9])
        with col:
            st.header("")
            st.header("")
            st.markdown(f"### {carmyear} {carbrand} {carmodel} {carvariant}")
            st.markdown(f"#### {carfuel} · {cartransmission} · {int(car['Kms'] / 1e3)}k kms")

    with col3:
        st.subheader("")
        st.write("")
        st.write("")
        st.markdown("#### Inspection date: " + carinfo['Inspection date'])
        st.markdown("#### Inspection time: " + carinfo['Inspection time'])
st.divider()
st.write(" ")

colored_header(label = "Inspection Timeline", description = "", color_name = "red-70")
st.write(" ")
col1, col2, col3, col4, col5 = st.columns([.21, .21, .22, .21, .15])
with col1:
    st.markdown("##### Interior Features")
with col2:
    st.markdown("##### Exterior Features") 
with col3:
    new_title = '<h5 style="font-family:sans-serif; color:Red;">Comfort Features</h5>'
    st.markdown(new_title, unsafe_allow_html = True) 
with col4:
    st.markdown("##### Safety Features")
with col5:
    st.markdown("##### Confirm Inspection")

inspection_progress_bar = st.progress(0, " ")
for percent_complete in range(48):
        time.sleep(0.0001)
        inspection_progress_bar.progress(percent_complete + 1, text = " ")

st.divider()
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
    st.subheader("Select the Comfort features available in the car: ")
    comfort_features = ['power steering', 'power windows front', 'power windows rear', 'air quality control', 'remote trunk opener', 'low fuel warning light',
                    'accessory power outlet', 'trunk light', 'vanity mirror', 'rear reading lamp', 'rear seat headrest', 'rear seat centre arm rest',
                    'height adjustable front seat belts', 'cup holders front', 'cup holders rear', 'seat lumbar support', 'multifunction steering wheel',
                    'cruise control', 'rear acvents', 'navigation system', 'smart access card entry', 'engine start stop button', 'glove box cooling',
                    'voice control', 'steering wheel gearshift paddles', 'steering mounted tripmeter', 'tailgate ajar', 'gear shift indicator',
                    'luggage hook and net', 'lane change indicator', 'drive modes', 'remote engine start stop', 'find my car location',
                    'remote horn light control', 'real time vehicle tracking', 'active noise cancellation', 'adjustable headrest', 'power boot',
                    'hands free tailgate']
    col1, col2, col3 = st.columns(3)
    collist = [col1, col2, col3]
    i = 0
    checkboxes = []
    for i, feat in enumerate(comfort_features):
        with collist[i % 3]:
            key = f"checkbox_{i}"
            checkbox = st.checkbox(label = feat.capitalize(), key = key)
            checkboxes.append(checkbox)
            i = i + 1

selected = []
st.header("")
confirm = st.columns(3)[1].button("Confirm", use_container_width = True, type = "primary")
if confirm:
    for box in checkboxes:
        selected.append(box)
    true_vals = [feature.capitalize() for feature in comfort_features if checkboxes[comfort_features.index(feature)] == True]
    st.session_state['comfort_features'] = true_vals
    st.toast("Comfort features recorded successfully")
    time.sleep(1)
    st.toast("Redirecting to Inspect Safety Features")
    time.sleep(2)
    switch_page("safetyfeatures")