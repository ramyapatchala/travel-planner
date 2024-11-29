import streamlit as st
import requests
import json

# Initialize session state for chat history and search history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

# Streamlit app title and sidebar filters
st.title("🌍 **Interactive Travel Guide Chatbot** 🤖")
st.markdown("Your personal travel assistant to explore amazing places.")

# Sidebar filters
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

# Function to get weather data
def get_weather(location, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    response = requests.get(url).json()
    
    if response.get("main"):
        # Convert temperatures from Kelvin to Celsius
        temp = response["main"]["temp"] - 273.15
        feels_like = response["main"]["feels_like"] - 273.15
        return {
            "location": location,
            "temperature": f"{temp:.1f}°C",
            "feels_like": f"{feels_like:.1f}°C",
            "weather": response["weather"][0]["description"].capitalize(),
            "humidity": f"{response['main']['humidity']}%",
        }
    else:
        return {"error": response.get("message", "Weather data not found.")}

# Function to display weather data
def display_weather(weather_data):
    if "error" in weather_data:
        st.error(weather_data["error"])
    else:
        st.markdown(f"### 🌤️ Weather in {weather_data['location']}")
        st.markdown(
            f"""
            - **Temperature:** {weather_data['temperature']}
            - **Feels Like:** {weather_data['feels_like']}
            - **Weather:** {weather_data['weather']}
            - **Humidity:** {weather_data['humidity']}
            """
        )

# Function to fetch places from Google Places API
def fetch_places_from_google(query):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": api_key}
    response = requests.get(base_url, params=params).json()
    return response.get("results", [])

# Function to display places
def display_places(places):
    st.markdown("### 📍 Top Recommendations")
    for place in places:
        st.markdown(f"**{place['name']}**")
        st.markdown(f"- 📍 Address: {place['formatted_address']}")
        st.markdown(f"- 🌟 Rating: {place.get('rating', 'N/A')}")

# Function to handle OpenAI response
def handle_function_calls(response_message):
    function_call = response_message.function_call
    function_args = json.loads(function_call.arguments)
    weather_data = None
    places = None
    
    # Fetch weather
    if "get_Weather" in function_args:
        location = function_args["get_Weather"]["location"]
        weather_data = get_weather(location, st.secrets["OpenWeatherAPIkey"])
        display_weather(weather_data)
    
    # Fetch places
    if "get_places_from_google" in function_args:
        query = function_args["get_places_from_google"]["query"]
        places = fetch_places_from_google(query)
        display_places(places)

# Input handling
user_query = st.text_input("🔍 Ask about places or weather:", value=selected_query)

if user_query:
    if user_query not in st.session_state["search_history"]:
        st.session_state["search_history"].append(user_query)

    # Store user message
    st.session_state['messages'].append({"role": "user", "content": user_query})

    # Get response (dummy response for illustration)
    response_message = {
        "function_call": {
            "name": "multi_Func",
            "arguments": json.dumps({
                "get_Weather": {"location": "San Francisco"},
                "get_places_from_google": {"query": "parks in New York"}
            })
        }
    }
    
    handle_function_calls(response_message)
