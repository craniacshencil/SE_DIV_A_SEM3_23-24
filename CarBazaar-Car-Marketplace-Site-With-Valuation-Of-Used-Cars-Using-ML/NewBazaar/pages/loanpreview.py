import streamlit as st
from streamlit_extras.colored_header import colored_header
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.switch_page_button import switch_page
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

#Checking Login Status
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

#Collapsing and removing sidebar, adding header image
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
        
st.columns(3)[1].image("images\\header.png", use_column_width="auto")

#Page Title
colored_header(
label = "Loan Calculator: ",
description = " ",
color_name = "red-70",
)

#Bringing in some session states
price = st.session_state['Price']
full_price = price * 1e5
values = st.session_state['values']

#Function for calculating loan details returns 3 values
def loan_amount(p,r,t):
    r = r / 1200
    m = t*12
    emi = (p*r*(1+r)**m) / ((1+r)**m-1)
    payable_interest = (emi*m) - p
    total_amount = emi*m 
    return emi, payable_interest, total_amount

#Display name of the car and sliders to give input for finance breakdown
st.markdown(f"## {values[1]} {values[0].capitalize()} {values[2].capitalize()} {values[3]} - ₹{price} Lakh")
st.divider()
col1, col2, col3 = st.columns([0.35, 0.4, 0.25])
with col1:
    st.subheader("")
    st.subheader("")
    st.write("")
    full_price = price * 1e5
    principal_in_lakhs = st.slider('Principal amount (in lakhs)',min_value=1.0, max_value= price, step = 0.1)
    principal = principal_in_lakhs * 100000 
    interest_rate = st.slider('Interest rate', min_value = 8.0, max_value=25.0, step = 0.5)
    term = st.slider('Term (in years)', min_value = 0.5, max_value = 10.0, step = 0.5)
    margin, col1 = st.columns([2, 3])
emi , payable_interest, total_amount = loan_amount(principal, interest_rate, term)

#Displaying doughnut chart breaking down the finances
with col2:
    labels = ['Down Payment', 'Principal Loan Amount', 'Interest Payable']
    label_val = [full_price - principal, principal, payable_interest]
    colors = ["#c48c12", "#ba3a3a", "#4f1b17"]
    fig = go.Figure(data = [go.Pie(labels = labels, values = label_val, hole = 0.5)])
    # fig = px.pie(names = labels, values = label_val, hole = 0.5, title = 'Finance Breakdown')
    fig.update_traces(marker=dict(colors=colors))
    fig.update_layout(legend=dict(x = 0, y = 1))
    st.plotly_chart(fig)

#Displaying important figures
with col3:
    st.title("")
    st.title("")
    st.title("")
    st.title("")
    if emi > 1e5:
        st.markdown(f"#### EMI : ₹{emi / 1e5:.2f} Lakh")
    else:
        st.markdown(f"#### EMI : ₹{emi / 1e3:.2f} Thousand")
    if total_amount > 1e7:
        st.markdown(f"#### Total amount: ₹{total_amount / 1e7:.2f} Cr")
    else:
        st.markdown(f"#### Total amount: ₹{total_amount / 1e5:.2f} Lakh")
    st.write("")
    if payable_interest > 1e5:
        st.markdown(f"##### Payable Interest: ₹{payable_interest / 1e5:.2f} Lakh")
    else:
        st.markdown(f"##### Payable Interest: ₹{payable_interest / 1e3:.2f} Thousand")
st.divider()

#Button for returning back to the listingpreview page
back = st.columns(7)[3].button("Return to listing")
if back:
    switch_page("listingpreview")