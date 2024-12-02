import streamlit as st
import requests
import json
from openai import OpenAI

# Initialize session state for itinerary and search history
if 'itinerary_bucket' not in st.session_state:
    st.session_state['itinerary_bucket'] = []
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

# Streamlit app title and sidebar filters
st.title("🌍 **Interactive Travel Planner** 🗺️")
st.markdown("Plan your perfect trip with ease!")

with st.sidebar:
    st.markdown("### Filters")
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.5, step=0.1)
    max_results = st.number_input("Max Results to Display", min_value=1, max_value=20, value=9)
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

# Generate itinerary using OpenAI API
def generate_itinerary():
    if not st.session_state['itinerary_bucket']:
        st.warning("No places in itinerary bucket!")
        return

    # Fetch details of the selected places
    places_details = []
    for place in st.session_state['itinerary_bucket']:
        places_details.append({
            "name": place["name"],
            "address": place.get("formatted_address", "No address available"),
            "rating": place.get("rating", "N/A"),
            "coordinates": place.get("geometry", {}).get("location", {})
        })

    # Prepare input for the OpenAI model
    itinerary_request = {
        "places": places_details,
        "start_time": "8:00 AM",  # Example start time
        "end_time": "8:00 PM",  # Example end time
    }

    messages = [
        {
            "role": "system",
            "content": "You are a travel planner. Plan a one-day itinerary based on the given places, start time, and end time. Consider time for transport and recommend time to spend at each location."
        },
        {
            "role": "user",
            "content": json.dumps(itinerary_request)
        }
    ]

    # Call OpenAI API
    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True  # Enable streaming for real-time display
        )

        # Display response in real-time
        st.markdown("### 🗺️ Your Itinerary")
        message_placeholder = st.empty()
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    except Exception as e:
        st.error(f"Error generating itinerary: {e}")

# Display results in a 3x3 tile layout
def display_results(results):
    col1, col2, col3 = st.columns(3)
    for idx, place in enumerate(results):
        col = [col1, col2, col3][idx % 3]
        with col:
            # Display place information
            st.image(
                place.get("photos", [{}])[0].get("photo_reference", "https://via.placeholder.com/400"),
                caption=place.get("name", "No Name"),
                use_column_width=True,
            )
            st.markdown(f"**{place.get('name', 'No Name')}**")
            st.markdown(f"🌟 Rating: {place.get('rating', 'N/A')}")
            lat, lng = place["geometry"]["location"].values()
            map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
            st.markdown(f"[📍 View on Map]({map_url})", unsafe_allow_html=True)

            # Add/remove itinerary button
            if place not in st.session_state['itinerary_bucket']:
                if st.button("Add to Itinerary", key=f"add_{idx}"):
                    st.session_state['itinerary_bucket'].append(place)
            else:
                st.markdown("✅ **Added to Itinerary**")
                if st.button("Remove", key=f"remove_{idx}"):
                    st.session_state['itinerary_bucket'].remove(place)

# Search and display places
user_query = st.text_input("🔍 Search for places (e.g., 'restaurants in New York'):", value=selected_query)
if user_query:
    if user_query not in st.session_state["search_history"]:
        st.session_state["search_history"].append(user_query)

    with st.spinner("Fetching results..."):
        search_results = fetch_places_from_google(user_query)

    if isinstance(search_results, dict) and "error" in search_results:
        st.error(search_results["error"])
    elif not search_results:
        st.warning("No places found matching your criteria.")
    else:
        display_results(search_results)

# Display itinerary bucket
if st.button("Show Itinerary Bucket"):
    st.markdown("### 🗺️ **Your Itinerary Bucket**")
    for idx, place in enumerate(st.session_state['itinerary_bucket']):
        st.write(f"{idx + 1}. {place['name']} - {place.get('formatted_address', 'No address available')}")

# Generate itinerary
if st.button("Generate Itinerary"):
    generate_itinerary()
