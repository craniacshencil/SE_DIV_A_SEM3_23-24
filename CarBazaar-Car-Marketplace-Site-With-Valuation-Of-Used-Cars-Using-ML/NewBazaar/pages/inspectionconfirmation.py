import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
from yaml.loader import SafeLoader
import time
from pymongo import MongoClient

#MongoConnection
client = MongoClient("localhost", 27017)
db = client.carbazaar
listings = db.post
appointments = db.appointment

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
st.header("Confirm Inspection <3/5>", divider = "red")
st.header("")
car = st.session_state['car_under_supervision']
carinfo = st.session_state['carinfo']
interiorfeatures = st.session_state['interior_features']
exteriorfeatures = st.session_state['exterior_features']
comfortfeatures = st.session_state['comfort_features']
safetyfeatures = st.session_state['safety_features']

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
     st.markdown("##### Comfort Features")
with col4:
    st.markdown("##### Safety Features")  
with col5:
    new_title = '<h5 style="font-family:sans-serif; color:Red;">Confirm Inspection</h5>'
    st.markdown(new_title, unsafe_allow_html = True)  

inspection_progress_bar = st.progress(0, " ")
for percent_complete in range(100):
        time.sleep(0.0001)
        inspection_progress_bar.progress(percent_complete + 1, text = " ")

st.divider()

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
st.header(" ")

confirminspection = st.columns(3)[1].button("Finalise Inspection", use_container_width = True, type = "primary")
if confirminspection:
    appointments.delete_one({"id_in_post" : car['_id']})
    filter = {"_id" : car['_id']}
    field_updates = {
        "Inspectionstatus" : "Inspection Successful",
        "Interiorfeatures" : interiorfeatures,
        "Exteriorfeatures" : exteriorfeatures,
        "Safetyfeatures" : safetyfeatures,
        "Comfortfeatures" : comfortfeatures
        }
    update = {"$set" : field_updates}
    listings.update_one(filter, update)
    st.success("Inspection succesful")
    time.sleep(1)
    st.toast("Redirecting to your dashboard")
    switch_page("supervisordashboard")

    


