import streamlit as st
import requests
import openai
import json
import time

# Initialize session state for chat history and search history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

# Streamlit app title and sidebar filters
st.title("🌍 **Interactive Travel Guide Chatbot** 🤖")
st.markdown("Your personal travel assistant to explore amazing places.")

with st.sidebar:
    st.markdown("### Filters")
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.5, step=0.1)
    max_results = st.number_input("Max Results to Display", min_value=1, max_value=20, value=10)
    st.markdown("___")
    st.markdown("### Search History")
    selected_query = st.selectbox("Recent Searches", options=[""] + st.session_state['search_history'])

# API keys
api_key = st.secrets["api_key"]
openai_api_key = st.secrets["key1"]

# Function to fetch places from Google Places API
def fetch_places_from_google(query):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            # Filter by minimum rating and limit results
            filtered_results = [place for place in results if place.get("rating", 0) >= min_rating]
            return filtered_results[:max_results]
        else:
            return {"error": f"API error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

# Function for interacting with OpenAI's API
def chat_completion_request(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            functions=[
                {
                    "name": "fetch_places_from_google",
                    "description": "Get details of places from Google Places API.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for Google Places API."}
                        },
                        "required": ["query"]
                    }
                }
            ],
            function_call="auto"
        )
        return response
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None

# Display chat history
for message in st.session_state['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
user_query = st.text_input("🔍 What are you looking for? (e.g., 'restaurants in Los Angeles'):", value=selected_query)

if user_query:
    if user_query not in st.session_state["search_history"]:
        st.session_state["search_history"].append(user_query)

    st.session_state['messages'].append({"role": "user", "content": user_query})

    # Get response from OpenAI
    with st.spinner("Generating response..."):
        response = chat_completion_request(st.session_state['messages'])

    if response:
        response_message = response["choices"][0]["message"]
        
        # Handle function call from GPT
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_args = json.loads(response_message["function_call"]["arguments"])
            if function_name == "fetch_places_from_google":
                query = function_args["query"]
                places = fetch_places_from_google(query)

                if isinstance(places, dict) and "error" in places:
                    st.error(f"Error: {places['error']}")
                elif not places:
                    st.warning("No places found matching your criteria.")
                else:
                    st.markdown("### 📍 Top Recommendations")
                    for idx, place in enumerate(places):
                        with st.expander(f"{idx + 1}. {place.get('name', 'No Name')}"):
                            st.write(f"📍 **Address**: {place.get('formatted_address', 'No address available')}")
                            st.write(f"🌟 **Rating**: {place.get('rating', 'N/A')} (Based on {place.get('user_ratings_total', 'N/A')} reviews)")
                            st.write(f"💲 **Price Level**: {place.get('price_level', 'N/A')}")
                            if "photos" in place:
                                photo_ref = place["photos"][0]["photo_reference"]
                                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}"
                                st.image(photo_url, caption=place.get("name", "Photo"), use_column_width=True)
                            lat, lng = place["geometry"]["location"].values()
                            map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
                            st.markdown(f"[📍 View on Map]({map_url})", unsafe_allow_html=True)
        
        else:
            st.session_state['messages'].append({"role": "assistant", "content": response_message["content"]})
            with st.chat_message("assistant"):
                st.markdown(response_message["content"])
