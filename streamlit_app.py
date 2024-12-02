
import streamlit as st
from streamlit_option_menu import option_menu
# Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Interactive Travel Guide Chatbot", page_icon="🌎", layout="wide")
page1 = st.Page("page1.py", title="Explore")
page2 = st.Page("page2.py", title="Itenary")
pg = st.navigation([page1, page2])
pg.run()
