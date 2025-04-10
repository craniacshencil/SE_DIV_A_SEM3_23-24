import streamlit as st
import pandas as pd
import time
import streamlit_authenticator as stauth
import yaml
from streamlit_extras.switch_page_button import switch_page
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from yaml.loader import SafeLoader
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
st.header("Delete listing", divider = "red")

#MongoDB config and bringing in the car to be deleted
client = MongoClient("localhost", 27017)
db = client.carbazaar
cars = db.post
wishlists = db.wishlist
car = st.session_state['deletedcar']
#content
finalsold = st.number_input(f"Enter the final selling price of your {car['Myear']} {car['Brand']} {car['Model']} {car['Variant']}",
                            value = None, placeholder = "Enter price in Lakh")
st.info("This is a compulsory field")
dummy = st.columns(7)[3].button(label = "Confirm Price", use_container_width = True)
if dummy:
    if finalsold != None:
        st.success("Listing deleted")
        st.success("Thank You for using CarBazaar")
        st.toast("Redirecting to My Listings in 3 seconds")
        time.sleep(3)
        #Converting Transmission and Fueltype back
        if car['Transmission'] == 'manual':
            car['Transmission'] = 0
        else:
                car['Transmission'] = 1

        if car['Fueltype'] == 'LPG':
                car['Fueltype'] = 0
        if car['Fueltype'] == 'CNG':
                car['Fueltype'] = 1
        if car['Fueltype'] == 'Petrol':
                car['Fueltype'] = 2
        if car['Fueltype'] == 'Diesel':
                car['Fueltype'] = 3
        if car['Fueltype'] == 'Electric':
                car['Fueltype'] = 4

        if car['Ownerno'] == "1st":
              car['Ownerno'] = 1
        if car['Ownerno'] == "2nd":
            car['Ownerno'] = 2
        if car['Ownerno'] == "3rd":
            car['Ownerno'] = 3
        if car['Ownerno'] == "4th":
              car['Ownerno'] = 4
        if car['Ownerno'] == "5th":
              car['Ownerno'] = 5
        if car['Ownerno'] == "6th":
              car['Ownerno'] = 6    
        #Adding cardata to the dataset, finding and deleting the car
        temp = pd.read_csv("data//train3.csv")
        search_data = temp.loc[(temp['model'] == car['Model'])
                            & (temp['variant'] == car['Variant'])
                        ]
        tc = temp['Turbo Charger'].mode()[0]
        kw = temp['Kerb Weight'].mean()
        dt = temp['Drive Type'].mode()[0]
        seats = temp['Seats'].mode()[0]
        tspeed = temp['Top Speed'].mean()
        acc = temp['Acceleration'].mean()
        doors = temp['Doors'].mode()[0]
        cvolume = temp['Cargo Volume'].mean()
        maxTorque = temp['Max Torque Delivered'].mean()
        measure = temp['avg_measure'].mean()
        feat = temp['Features'].mode()[0]
        valves = temp['Valves'].mode()[0]
        tread = temp['Tread'].mean()

        car_values = [
            car['Myear'], car['Transmission'],
            car['Fueltype'], car['Kms'],
            tc, kw, dt, seats, tspeed, acc, doors,
            cvolume, car['Ownerno'], maxTorque,
            finalsold * 1e5, measure, feat, valves, tread
        ]

        df = pd.read_csv("data//pred_data.csv")
        df.loc[len(df), :] = car_values
        df.to_csv("pred_data.csv", index = False)
        cars.delete_one({'_id' : ObjectId(car['_id'])})
        wishlists.delete_one({'id_in_post' : ObjectId(car['_id'])})
        switch_page("mylisting")
    else:
        st.error("Enter a price")
        