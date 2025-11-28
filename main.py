import streamlit as st
import time
import requests
from app.chat_utils import get_chat_model, ask_chat_model
from app.config import EURI_API_KEY, OPENWEATHER_API_KEY

# Page config
st.set_page_config(
    page_title="🌱 Farm Mate - Farmer Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .chat-message.user { background-color: #2e7d32; color: white; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
    .chat-message.assistant { background-color: #f1f8e9; color: black; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_model" not in st.session_state:
    st.session_state.chat_model = get_chat_model(EURI_API_KEY)

# Header
st.markdown("""
<div style="text-align:center; padding:1.5rem;">
    <h1 style="color:#2e7d32;">🌱 Farm Mate </h1>
    <p>Your Intelligent Farming Assistant 🌾</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🌿 Settings")
    crop_choice = st.selectbox("Select a crop", ["🍇 Grapes","🌾 Wheat", "🌽 Maize", "🥔 Potato", "🍅 Tomato", "🍚 Rice", "🧅 Onion","🌶️ Chili","🥒 Cucumber","🥦 Cauliflower","🥕 Carrot","🍆 Brinjal (Eggplant)","🥭 Mango","🍌 Banana","🥜 Groundnut","🌻 Sunflower","🌴 Coconut","🍬 Sugarcane","🫘 Soybean","🍊 Orange", "Other"])
    location = st.text_input("📍 Enter your district/city", "Solapur")
    
    # Weather API call
    def get_weather(city):
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        try:
            response = requests.get(url)
            data = response.json()
            if data.get("cod") != "200":
                return None
            return data
        except:
            return None
    
    weather_data = None
    if st.button("☁️ Get Weather Forecast"):
        with st.spinner("Fetching weather..."):
            weather_data = get_weather(location)
            if weather_data:
                today = weather_data["list"][0]
                st.success(f"🌦 Weather in {location}: {today['weather'][0]['description'].title()}, 🌡 {today['main']['temp']}°C")
                st.markdown("#### 📅 Next 5 Days")
                for i in range(0, 40, 8):  # every 24 hours
                    day = weather_data["list"][i]
                    date = day["dt_txt"].split(" ")[0]
                    desc = day["weather"][0]["description"].title()
                    temp = day["main"]["temp"]
                    st.write(f"**{date}** → {desc}, 🌡 {temp}°C")
            else:
                st.error("⚠️ Could not fetch weather. Please check city name or API key.")

# Display chat
st.markdown("### 💬 Chat with Farm Mate ")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.caption(message["timestamp"])

# Chat input
if prompt := st.chat_input("Ask Farm Mate  about crops, weather, or farming..."):
    timestamp = time.strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp})
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(timestamp)

    # Assistant reply
    with st.chat_message("assistant"):
        with st.spinner("🌾 Thinking..."):
            weather_context = ""
            if weather_data:
                today_weather = weather_data["list"][0]
                weather_context = f"""
                Current Weather in {location}: {today_weather['weather'][0]['description']} with temperature {today_weather['main']['temp']}°C.
                """
            
            system_prompt = f"""
            You are Farm Mate , a friendly farming assistant for Indian farmers.
            Crop selected: {crop_choice}.
            Use weather info if available.

            {weather_context}

            User Question: {prompt}

            Answer:
            """
            response = ask_chat_model(st.session_state.chat_model, system_prompt)
        
        st.markdown(response)
        st.caption(timestamp)
        st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center; color:#666;'>🤖 Powered by Dnyaneshwar Bhosale | 🌱 Helping Farmers Grow Better</div>", unsafe_allow_html=True)
