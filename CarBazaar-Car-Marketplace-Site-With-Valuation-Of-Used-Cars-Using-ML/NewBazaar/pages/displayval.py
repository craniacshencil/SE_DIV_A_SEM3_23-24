import streamlit as st
import time
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container 

#Collapse and remove sidebar, add header image
st.set_page_config(initial_sidebar_state = "collapsed", layout = "wide")
st.columns(3)[1].image("images\header.png", use_column_width="auto")
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

#Initializing, setting session states and related variables
pred = st.session_state['pred']
values = st.session_state['values']
st.session_state['Price'] = "Not initialized"
if 'price_entry' not in st.session_state:
    st.session_state.price_entry = False
def enable_price_entry():
    st.session_state.price_entry = True
lb = pred - pred * 8/100
ub = pred + pred * 4/100

#Content
st.header("Suggested Valuation: ", divider = "red")
 #Displaying the price range
with stylable_container(
    key="container_with_border",
    css_styles="""
        {
            border: 2px solid rgba(235, 64, 52, 1);
            border-radius: 1rem;
            padding: calc(1em - 1px)
        }
        """,
):

    st.header(" ")
    car_name = f"{values[0].capitalize()} {values[2].capitalize()}, {values[1]}"
    car_specs = f"{values[3]} variant · {values[7]} kms"
    col1, col2, col3 = st.columns([4, 2, 3])
    with col2:
        st.write(car_name)
        st.caption(car_specs)
    st.title(" ")
    col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])
    with col2:
        if lb > 1e7:
            st.subheader(f"₹{round(lb/1e7, 2)} Cr")
        elif lb > 1e5:
            st.subheader(f"₹{round(lb/1e5, 2)} Lakh")
        
    with col4:
        if ub > 1e7:
            st.subheader(f"₹{round(ub/1e7, 2)} Cr")
        elif ub > 1e5:
            st.subheader(f"₹{round(ub/1e5, 2)} Lakh")
        
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        colored_header(label = " ",
                    description = " ", 
                    color_name = 'red-70')
    st.header(" ")  
    st.header(" ")

    #Continue to list and finalized price input
    col1, col2, col3 = st.columns([5, 2, 4])
    with col2:
        to_list = st.button("Proceed to list", on_click = enable_price_entry)   
if st.session_state.price_entry:
    st.divider() 
    col1, col2, col3 = st.columns([2, 7, 2])
    with col2:
            price = st.number_input("Enter price in Lakh: ", min_value = round(lb/1e5, 2), max_value = round(ub/1e5, 2), step = 0.01
                                    , placeholder = "Enter price here...", value = None)
            st.info("The price should lie between the suggested range.")
    if price != None:
        col1, col2 = st.columns([3, 5])
        with col2:
            st.write(" ")
            st.subheader(f"Finalized Price: {price} Lakh.")
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        with col2:
            st.write(" ")
            finale = st.button("Upload images", use_container_width = True, type = 'primary')
            if finale:
                st.session_state['Price'] = price
                with st.spinner("Redirecting to upload images...."):
                    time.sleep(2)
                    switch_page("imgupload")
            with col3:
                st.write(" ")
                back = st.button("Back", use_container_width = True)
                if back:
                    switch_page("valuation")
