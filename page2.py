import streamlit as st
import requests

# Initialize session state for itinerary bucket and search history
if 'itinerary_bucket' not in st.session_state:
    st.session_state['itinerary_bucket'] = []
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

# Streamlit app title and sidebar filters
st.title("🌍 **Travel Planner** ✈️")
st.markdown("Discover amazing places and plan your trip effortlessly!")

with st.sidebar:
    st.markdown("### Filters")
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.5, step=0.1)
    max_results = st.number_input("Max Results to Display", min_value=1, max_value=20, value=9)
    st.markdown("___")
    st.markdown("### Search History")
    selected_query = st.selectbox("Recent Searches", options=[""] + st.session_state['search_history'])

# API key for Google Places API
api_key = st.secrets["api_key"]

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

# Display places in 3x3 grid layout
def display_places_grid(places):
    cols = st.columns(3)
    for idx, place in enumerate(places):
        with cols[idx % 3]:
            # Display place information in a tile
            name = place.get("name", "No Name")
            lat, lng = place["geometry"]["location"].values()
            map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
            photo_url = None
            if "photos" in place:
                photo_ref = place["photos"][0]["photo_reference"]
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}"

            if photo_url:
                st.image(photo_url, caption=name, use_column_width=True)
            else:
                st.write(name)

            st.markdown(f"[📍 View on Map]({map_url})", unsafe_allow_html=True)

            # Display "Add to Itinerary" or "Added" button
            if name in st.session_state['itinerary_bucket']:
                st.button("Added", disabled=True, key=f"added_{idx}")
            else:
                if st.button("Add to Itinerary", key=f"add_{idx}"):
                    st.session_state['itinerary_bucket'].append(name)

# Generate itinerary based on selected places
def generate_itinerary():
    if not st.session_state['itinerary_bucket']:
        st.warning("No places in itinerary bucket!")
        return
    st.markdown("### 🗺️ Your Itinerary")
    for idx, place in enumerate(st.session_state['itinerary_bucket'], start=1):
        st.markdown(f"{idx}. **{place}**")

# Handle search input
user_query = st.text_input("🔍 Search for places (e.g., 'restaurants in Paris'):", value=selected_query)

if user_query:
    if user_query not in st.session_state["search_history"]:
        st.session_state["search_history"].append(user_query)

    st.markdown(f"### Results for: **{user_query}**")
    with st.spinner("Fetching places..."):
        places_data = fetch_places_from_google(user_query)

    if isinstance(places_data, dict) and "error" in places_data:
        st.error(f"Error: {places_data['error']}")
    elif not places_data:
        st.warning("No places found matching your criteria.")
    else:
        display_places_grid(places_data)

# Show itinerary bucket
st.markdown("### 📋 Itinerary Bucket")
if st.session_state['itinerary_bucket']:
    for place in st.session_state['itinerary_bucket']:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(place)
        with col2:
            if st.button("Remove", key=f"remove_{place}"):
                st.session_state['itinerary_bucket'].remove(place)
else:
    st.write("Your itinerary bucket is empty.")

# Generate itinerary button
if st.button("Generate Itinerary"):
    generate_itinerary()
