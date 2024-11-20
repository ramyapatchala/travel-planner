import streamlit as st
import requests

# Chatbot interface title
st.title("Travel Guide Chatbot 🤖")

# Google Places API Key (replace with your actual key)
api_key = st.secrets['api_key']

# Function to fetch data from Google Places API
def fetch_places_from_google(query, api_key):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key
    }

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

# Chatbot input field
user_query = st.text_input("Ask me about places to visit (e.g., 'parks in Syracuse'):", "")

# Trigger API call when a query is entered
if user_query:
    st.write(f"Fetching details for: **{user_query}**...")
    places_data = fetch_places_from_google(user_query, api_key)

    # Display fetched places
    if "error" in places_data:
        st.write(f"Error fetching data: {places_data['error']}")
    else:
        st.write("Here are some places I found:")
        results = places_data.get("results", [])
        if results:
            for place in results:
                st.write(f"**{place.get('name', 'No Name')}**")
                st.write(f"📍 Address: {place.get('formatted_address', 'No address available')}")
                st.write(f"🌟 Rating: {place.get('rating', 'N/A')} (Based on {place.get('user_ratings_total', 'N/A')} reviews)")
                st.write("---")
        else:
            st.write("No places found for the given query.")
