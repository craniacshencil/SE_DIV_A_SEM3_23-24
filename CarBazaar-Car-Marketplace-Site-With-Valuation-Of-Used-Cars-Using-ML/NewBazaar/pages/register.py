import streamlit as st
import streamlit_authenticator as stauth
import yaml
import time
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

registered_successfully = False

try:
    if authenticator.register_user('Register user', preauthorization=False):
        st.success('User registered successfully')
        registered_successfully = True
except Exception as e:
    st.error(e)

if registered_successfully:
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    st.toast("Redirecting to login in 3 sec..")
    time.sleep(4)
    switch_page("login")

st.text("")
st.text("")

st.write("Already registered?")
if st.button("Login"):
    switch_page("login")
