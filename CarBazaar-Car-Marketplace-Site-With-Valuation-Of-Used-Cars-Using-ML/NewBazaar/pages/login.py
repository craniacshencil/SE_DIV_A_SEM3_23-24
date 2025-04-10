import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_extras.switch_page_button import switch_page

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

st.columns(3)[1].image("images\\header.png",use_column_width="auto")

name, authentication_status, username= authenticator.login('Login', 'main')
if username == "admin2":
    switch_page("adminapproval")
if username == "supervisor2":
    switch_page("supervisordashboard")
if authentication_status:
    authenticator.logout('Logout', 'main')
    # st.write(f'Welcome *{name}*')
    switch_page("dashboard")
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')


st.text("")
st.text("")

st.write("New here?")
if st.button("Sign up"):
    switch_page("Register")
