import streamlit as st
import requests
import json
from datetime import datetime
from openai import OpenAI

# Initialize session state for itinerary and search results
if "itinerary_bucket" not in st.session_state:
    st.session_state["itinerary_bucket"] = []
if "search_history" not in st.session_state:
    st.session_state["search_history"] = []

# Streamlit app title and sidebar filters
st.title("🌍 **Interactive Travel Planner** 🗺️")
st.markdown("Plan your perfect day trip with curated recommendations!")

with st.sidebar:
    st.markdown("### Filters")
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.5, step=0.1)
    max_results = st.number_input("Max Results to Display", min_value=1, max_value=20, value=9)
    st.markdown("___")
    st.markdown("### Search History")
    selected_query = st.selectbox("Recent Searches", options=[""] + st.session_state["search_history"])
    st.markdown("___")
    if st.button("View Itinerary"):
        st.markdown("### 🛤️ Current Itinerary")
        if not st.session_state["itinerary_bucket"]:
            st.warning("Your itinerary is empty!")
        else:
            for place in st.session_state["itinerary_bucket"]:
                st.write(f"- **{place['name']}** ({place.get('rating', 'N/A')} 🌟)")

        if st.button("Clear Itinerary"):
            st.session_state["itinerary_bucket"] = []
            st.success("Itinerary cleared!")

# API keys
api_key = st.secrets["api_key"]
openai_api_key = st.secrets["key1"]

# Google Places Photo API URL constructor
def get_photo_url(photo_reference):
    if photo_reference:
        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}"
    return "https://via.placeholder.com/400"  # Fallback for missing images

# Function to fetch places from Google Places API
def fetch_places_from_google(query):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": api_key}
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

# Display results in a 3x3 grid
def display_results(results):
    cols = st.columns(3)
    for idx, place in enumerate(results):
        col = cols[idx % 3]
        with col:
            photo_reference = (
                place.get("photos", [{}])[0].get("photo_reference") if place.get("photos") else None
            )
            photo_url = get_photo_url(photo_reference)

            st.image(photo_url, caption=place.get("name", "No Name"), use_column_width=True)
            st.markdown(f"**{place.get('name', 'No Name')}**")
            st.markdown(f"🌟 Rating: {place.get('rating', 'N/A')}")
            lat, lng = place["geometry"]["location"].values()
            map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
            st.markdown(f"[📍 View on Map]({map_url})", unsafe_allow_html=True)

            if place not in st.session_state["itinerary_bucket"]:
                if st.button("Add to Itinerary", key=f"add_{idx}"):
                    st.session_state["itinerary_bucket"].append(place)
            else:
                st.markdown("✅ **Added to Itinerary**")
                if st.button("Remove", key=f"remove_{idx}"):
                    st.session_state["itinerary_bucket"].remove(place)

# Function to generate an itinerary
def generate_itinerary(places):
    if not places:
        return "Your itinerary is empty!"
    itinerary_data = [
        {
            "name": place["name"],
            "address": place.get("formatted_address", "Address not available"),
            "rating": place.get("rating", "N/A"),
            "location": place["geometry"]["location"]
        }
        for place in places
    ]

    prompt = (
        f"Plan a one-day itinerary starting at 9:00 AM with the following places. "
        f"Include approximate travel times and suggest how long to spend at each place. "
        f"Here are the places:\n{json.dumps(itinerary_data, indent=2)}"
    )

    client = OpenAI(api_key=openai_api_key)
    response = client.completions.create(
        model="gpt-4o",
        prompt=prompt,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].text.strip()

# Search for places
user_query = st.text_input("🔍 Search for places (e.g., 'restaurants in Los Angeles'):", value=selected_query)

if user_query:
    if user_query not in st.session_state["search_history"]:
        st.session_state["search_history"].append(user_query)

    with st.spinner("Searching for places..."):
        search_results = fetch_places_from_google(user_query)

    if isinstance(search_results, dict) and "error" in search_results:
        st.error(search_results["error"])
    elif not search_results:
        st.warning("No places found matching your criteria.")
    else:
        st.markdown("### 📍 Recommended Places")
        display_results(search_results)

# Generate itinerary button
if st.button("Generate Itinerary"):
    with st.spinner("Creating your itinerary..."):
        itinerary = generate_itinerary(st.session_state["itinerary_bucket"])
    st.markdown("### 🗓️ Your One-Day Itinerary")
    st.markdown(itinerary)
