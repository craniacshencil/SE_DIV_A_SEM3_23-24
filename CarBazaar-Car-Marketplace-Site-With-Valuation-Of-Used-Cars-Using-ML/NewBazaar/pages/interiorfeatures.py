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

#MongoConnection
client = MongoClient("localhost", 27017)
db = client.carbazaar
appointments = db.appointment
#Header Text
st.header("Interior features <1/5>", divider = "red")
st.header("")
car = st.session_state['car_under_supervision']
st.session_state['interior_features'] = "Not set"
st.session_state['carinfo'] = "Not set"

#Fetching the display image
url = car['Displayimage']
response = requests.get(url, stream = True)
if response.status_code == 200:
    display_image = Image.open(BytesIO(response.content))

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
    appointment = appointments.find_one({"id_in_post" : car['_id']})
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
        st.image(display_image)
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
        st.markdown("#### Inspection date: " + appointment['Inspection date'])
        st.markdown("#### Inspection time: " + appointment['Inspection time'])
st.divider()
st.write(" ")
colored_header(label = "Inspection Timeline", description = "", color_name = "red-70")
st.write(" ")
col1, col2, col3, col4, col5 = st.columns([.21, .21, .22, .21, .15])
with col1:
    new_title = '<h5 style="font-family:sans-serif; color:Red;">Interior Features</h5>'
    st.markdown(new_title, unsafe_allow_html = True)
with col2:
    st.markdown("##### Exterior Features") 
with col3:
    st.markdown("##### Comfort Features")
with col4:
    st.markdown("##### Safety Features")
with col5:
    st.markdown("##### Confirm Inspection")

inspection_progress_bar = st.progress(0, " ")
for percent_complete in range(5):
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
    st.subheader("Select the Interior features available in the car: ")
    interior_features = ['air conditioner', 'adjustable steering', 'digital odometer', 'tachometer', 'electronic multi tripmeter', 'leather seats',
                        'fabric upholstery', 'leather steering wheel', 'glove compartment', 'digital clock', 'outside temperature display', 'cigarette lighter',
                        'rear folding table', 'driving experience control eco', 'height adjustable driver seat', 'ventilated seats', 'dual tone dashboard',
                        'leather wrap gear shift selector']
    col1, col2, col3 = st.columns(3)
    collist = [col1, col2, col3]
    i = 0
    checkboxes = []
    for i, feat in enumerate(interior_features):
        with collist[i % 3]:
            key = f"checkbox_{i}"
            checkbox = st.checkbox(label = feat.capitalize(), key = key)
            checkboxes.append(checkbox)
            i = i + 1

    selected = []
st.header("")

#Saving details from DB in a dictionary
car_info = {
    "Display image" : display_image,
    "Inspection date" : appointment['Inspection date'],
    "Inspection time" : appointment['Inspection time']
}
st.session_state['carinfo'] = car_info

confirm = st.columns(3)[1].button("Confirm", use_container_width = True, type = "primary")
if confirm:
    for box in checkboxes:
        selected.append(box)
    true_vals = [feature.capitalize() for feature in interior_features if checkboxes[interior_features.index(feature)] == True]
    st.session_state['interior_features'] = true_vals
    st.toast("Interior features recorded successfully")
    time.sleep(1)
    st.toast("Redirecting to Inspect Exterior Features")
    time.sleep(2)
    switch_page("exteriorfeatures")



     