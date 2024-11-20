import streamlit as st
import requests

# App title
st.title("🌍 **Interactive Travel Guide Chatbot** 🤖")
st.markdown("Your personal travel assistant to explore amazing places.")

# Sidebar for additional functionalities
with st.sidebar:
    st.markdown("### Filters")
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.5, step=0.1)
    max_results = st.number_input("Max Results to Display", min_value=1, max_value=20, value=10)
    st.markdown("___")

    st.markdown("### Search History")
    search_history = st.session_state.get("search_history", [])
    if search_history:
        selected_query = st.selectbox("Recent Searches", options=[""] + search_history)
    else:
        selected_query = None

# Save query history in session state
if "search_history" not in st.session_state:
    st.session_state["search_history"] = []

# Google Places API Key
api_key = st.secrets["api_key"]

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

# Chatbot Input
user_query = st.text_input("🔍 What are you looking for? (e.g., 'restaurants in Los Angeles'):", "")

# Re-use query from search history when selected
if selected_query:
    user_query = selected_query

if user_query:
    # Save query in search history
    if user_query not in st.session_state["search_history"]:
        st.session_state["search_history"].append(user_query)

    with st.spinner("Fetching amazing places..."):
        places_data = fetch_places_from_google(user_query, api_key, min_rating, max_results)

    # Display results
    if isinstance(places_data, dict) and "error" in places_data:
        st.error(f"Error: {places_data['error']}")
    elif not places_data:
        st.warning("No places found matching your criteria.")
    else:
        # Tabs for results
        st.markdown("### 📍 Top Recommendations")
        for idx, place in enumerate(places_data):
            with st.expander(f"{idx + 1}. {place.get('name', 'No Name')}"):
                # Show place details
                st.write(f"📍 **Address**: {place.get('formatted_address', 'No address available')}")
                st.write(f"🌟 **Rating**: {place.get('rating', 'N/A')} (Based on {place.get('user_ratings_total', 'N/A')} reviews)")
                st.write(f"💲 **Price Level**: {place.get('price_level', 'N/A')}")
                # Show a photo if available
                if "photos" in place:
                    photo_reference = place["photos"][0]["photo_reference"]
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}"
                    st.image(photo_url, caption=place.get("name", "Photo"), use_column_width=True)
                # Map link
                lat = place["geometry"]["location"]["lat"]
                lng = place["geometry"]["location"]["lng"]
                map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
                st.markdown(f"[📍 View on Map]({map_url})", unsafe_allow_html=True)

# Footer for User Feedback
st.markdown("---")
st.markdown("### 💬 Feedback")
feedback = st.text_area("Tell us how we can improve:")
if st.button("Submit Feedback"):
    if feedback.strip():
        st.success("Thank you for your feedback!")
    else:
        st.error("Please enter some feedback before submitting.")
