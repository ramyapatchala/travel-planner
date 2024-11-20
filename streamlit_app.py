
import streamlit as st
from streamlit_option_menu import option_menu

import streamlit as st

# Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Interactive Travel Guide Chatbot", page_icon="🌎", layout="wide")

# Import your app logic or pages
exec(open("page1.py").read())
