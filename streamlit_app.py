
import streamlit as st
from streamlit_option_menu import option_menu

# Set up a sidebar or navigation for different pages
st.set_page_config(page_title="Multi-Page App", layout="wide")

# Define navigation using a simple option menu
with st.sidebar:
    selected_page = option_menu(
        "Select Lab",
        ["Manual & AI Assisted Editting", "Second Lab", "Third Lab", "Fourth Lab", "Fifth Lab"],
        icons=['book', 'book', 'book','book', 'book'],
        menu_icon="cast", 
        default_index=0,
    )

# Load the appropriate page based on the user's selection
if selected_page == "Manual & AI Assisted Editting":
    st.title("First Lab")
    # Execute the Lab1.py code
    exec(open("page1.py").read())  # This will run the content of Lab1.py

elif selected_page == "Second Lab":
    st.title("Second Lab")
    # Execute the Lab2.py code
    exec(open("Lab2.py").read())  # This will run the content of Lab2.py

elif selected_page == "Third Lab":
    st.title("Third Lab")
    # Execute the Lab3.py code
    exec(open("Lab3.py").read())  # This will run the content of Lab3.py
