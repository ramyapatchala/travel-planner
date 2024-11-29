import streamlit as st
import requests
import json
from openai import OpenAI

# Initialize session state for chat and search history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .assistant { color: #4CAF50; font-weight: bold; }
    .user { color: #2196F3; font-weight: bold; }
    .chat-box { background-color: #f1f1f1; padding: 10px; border-radius: 10px; }
    .expander-header { font-weight: bold; font-size: 16px; }
    .place-details { margin: 5px 0; }
    .place-title { font-size: 18px; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit app title and sidebar filters
st.title("🌍 **Interactive Travel Guide Chatbot** 🤖")
st.markdown("Your personal AI assistant to explore and discover amazing places worldwide.")

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔧 Filters")
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.5, step=0.1)
    max_results = st.number_input("Max Results to Display", min_value=1, max_value=20, value=10)
    st.markdown("### 📂 Search History")
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
            filtered_results = [place for place in results if place.get("rating", 0) >= min_rating]
            return filtered_results[:max_results]
        else:
            return {"error": f"API error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

# Function for OpenAI chat completion
def chat_completion_request(messages):
    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            functions=[
                {
                    "name": "fetch_places_from_google",
                    "description": "Get details of places like hotels, restaurants, and tourist attractions from Google Places API.",
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
    role = "assistant" if message["role"] == "assistant" else "user"
    icon = "🤖" if role == "assistant" else "👤"
    st.markdown(f"<div class='chat-box'><b class='{role}'>{icon} {role.capitalize()}:</b><br>{message['content']}</div>", unsafe_allow_html=True)

# User input and query handling
user_query = st.text_input("🔍 Ask your travel assistant (e.g., 'best restaurants in Paris'):", value=selected_query)

if user_query:
    if user_query not in st.session_state["search_history"]:
        st.session_state["search_history"].append(user_query)

    st.session_state['messages'].append({"role": "user", "content": user_query})

    # Generate response
    with st.spinner("Generating response..."):
        response = chat_completion_request(st.session_state['messages'])

    if response:
        response_message = response.choices[0].message

        # Handle function call
        if response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)
            if function_name == "fetch_places_from_google":
                query = function_args["query"]
                places = fetch_places_from_google(query)

                # Display places
                if isinstance(places, dict) and "error" in places:
                    st.error(f"Error: {places['error']}")
                elif not places:
                    st.warning("No places found matching your criteria.")
                else:
                    st.markdown("## 📍 Top Recommendations")
                    for idx, place in enumerate(places):
                        with st.expander(f"{idx + 1}. {place.get('name', 'No Name')}", expanded=True):
                            st.markdown(f"**Address**: {place.get('formatted_address', 'No address available')}")
                            st.markdown(f"**Rating**: 🌟 {place.get('rating', 'N/A')} (Based on {place.get('user_ratings_total', 'N/A')} reviews)")
                            st.markdown(f"**Price Level**: 💲 {place.get('price_level', 'N/A')}")
                            if "photos" in place:
                                photo_ref = place["photos"][0]["photo_reference"]
                                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}"
                                st.image(photo_url, caption=place.get("name", "Photo"), use_column_width=True)
                            lat, lng = place["geometry"]["location"].values()
                            st.markdown(f"[📍 View on Map](https://www.google.com/maps/search/?api=1&query={lat},{lng})", unsafe_allow_html=True)

        else:
            st.session_state['messages'].append({"role": "assistant", "content": response_message.content})
            st.markdown(f"<div class='chat-box'><b class='assistant'>🤖 Assistant:</b><br>{response_message.content}</div>", unsafe_allow_html=True)
