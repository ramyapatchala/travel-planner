import streamlit as st
from openai import OpenAI, OpenAIError
import requests

# App title
st.title("🌍 **Travel Guide Chatbot with GPT-4** 🤖")
st.markdown("Your travel assistant powered by Google Places and GPT-4.")

# Sidebar for customization
with st.sidebar:
    st.title("🔧 Customize Your Experience")
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.5, step=0.1)
    max_results = st.number_input("Max Results to Display", min_value=1, max_value=20, value=10)

# OpenAI API key
openai_api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=openai_api_key)
# Function to fetch data from Google Places API
def fetch_places_from_google(query, api_key, min_rating, max_results):
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
            # Filter by minimum rating
            filtered_results = [place for place in results if place.get("rating", 0) >= min_rating]
            return filtered_results[:max_results]
        else:
            return {"error": f"API error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

# Function to query OpenAI GPT-4
def query_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response
    except Exception as e:
        return f"Error querying OpenAI: {str(e)}"

# Chatbot Input
user_query = st.text_input("🔍 Ask me anything about travel (e.g., 'What are the best parks in NYC?'):")

if user_query:
    with st.spinner("Thinking..."):
        # Query GPT-4
        gpt_response = query_openai(user_query)
        st.markdown("### 🤖 GPT-4's Answer:")
        st.write(gpt_response)

        # Fetch additional structured data
        google_places_api_key = st.secrets["api_key"]
        places_data = fetch_places_from_google(user_query, google_places_api_key, min_rating, max_results)

        # Display results
        st.markdown("### 📍 Top Recommendations from Google Places:")
        if isinstance(places_data, dict) and "error" in places_data:
            st.error(f"Error: {places_data['error']}")
        elif not places_data:
            st.warning("No places found matching your criteria.")
        else:
            for idx, place in enumerate(places_data):
                with st.expander(f"{idx + 1}. {place.get('name', 'No Name')}"):
                    st.write(f"📍 **Address**: {place.get('formatted_address', 'No address available')}")
                    st.write(f"🌟 **Rating**: {place.get('rating', 'N/A')} (Based on {place.get('user_ratings_total', 'N/A')} reviews)")
                    st.write(f"💲 **Price Level**: {place.get('price_level', 'N/A')}")
                    if "photos" in place:
                        photo_reference = place["photos"][0]["photo_reference"]
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={google_places_api_key}"
                        st.image(photo_url, caption=place.get("name", "Photo"), use_column_width=True)
                    lat = place["geometry"]["location"]["lat"]
                    lng = place["geometry"]["location"]["lng"]
                    map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
                    st.markdown(f"[📍 View on Map]({map_url})", unsafe_allow_html=True)
