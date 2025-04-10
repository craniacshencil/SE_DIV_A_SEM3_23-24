import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import base64
from st_clickable_images import clickable_images

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

#Adding phone no
username = st.session_state['username']
def add_phone_number(username, phone_number):
    if username in config['credentials']['usernames']:
        config["credentials"]["usernames"][username]["phone_number"] = int(phone_number)
    else:
        print(f"User {username} not found.")
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

st.columns(3)[1].image("images\\header.png" ,use_column_width="auto")

#Checking if user has phone number
number_exists = False
if "phone_number" in config["credentials"]["usernames"][username]:
    number_exists = True
    st.session_state['phonenumber'] = config["credentials"]["usernames"][username]["phone_number"]

#NavBar config
nav_bar = option_menu(None, ["Home", "Check Valuation", "Buy", "My Listings", "Wishlist", "Book Inspection"],
    icons=["house-fill", 'cash-coin', "car-front", "bag", "bookmark-heart-fill", "tools"],
    menu_icon="cast", default_index = 0, orientation="horizontal")
if ((nav_bar == "Wishlist") & (number_exists)):
    switch_page("wishlist")
if ((nav_bar == "My Listings") & (number_exists)):
    switch_page("mylisting")
if ((nav_bar == "Check Valuation") & (number_exists)):
    switch_page("valuation")
if ((nav_bar == "Buy") & (number_exists)):
    switch_page("listings")
if((nav_bar == "Book Inspection") & (number_exists)):
    switch_page("bookinspection")
if ((nav_bar == "Wishlist") | (nav_bar == "Check Valuation") | (nav_bar == "Buy") | (nav_bar == "My Listings") & (not number_exists)):
    st.error("Enter your phone number")

if not number_exists:
    phonenumber = st.text_input("Please Enter Phone Number: ")
    if st.button("Confirm Number"):
        add_phone_number(username, phonenumber)
        st.success("Phone number added to account.")
        st.session_state['phonenumber'] = config["credentials"]["usernames"][username]["phone_number"]
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
#Content
col1, col2 = st.columns([0.05, 0.95])
with col2:
    images = []
    for file in ["images//buy_now.png", "images//sell_ride.png"]:
        with open(file, "rb") as image:
            encoded = base64.b64encode(image.read()).decode()
            images.append(f"data:image/jpeg;base64,{encoded}")

    clicked = clickable_images(
        images,
        titles = ["buy", "sell"],
        div_style = {"display": "block", "justify-content": "flex-start", "flex-wrap": "nowrap", "width" : "1200px"},
        img_style = {"margin": "1px", "height": "590px", "width" : "590px"},
    )
    # st.write(f"username: {st.session_state['username']}")
    # if "phonenumber" in st.session_state:
    #     st.write(f"phonenumber: {st.session_state['phonenumber']}")
    # else:
    #     st.write("Current user does not have a registered phone number")
    if ((clicked == 0) & number_exists):
          switch_page("listings")
    if ((clicked == 1) & number_exists):
          switch_page("valuation")
