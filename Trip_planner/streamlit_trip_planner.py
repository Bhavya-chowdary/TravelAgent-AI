"""
Streamlit UI for Trip Planner 3
Simple and interactive travel itinerary generator
"""

import streamlit as st
from trip_planner3 import generate_trip_itinerary
from datetime import datetime

# Page configurations
st.set_page_config(
    page_title="✈️ Trip Planner AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        background-color: #FF6B6B;
        color: white;
        font-size: 18px;
        padding: 10px 30px;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #FF5252;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("✈️ AI Trip Planner")
st.markdown("### Plan your trip perfectly with AI-powered itinerary generation")
st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.header("📍 Trip Details")
    
    # Destination input
    destination = st.text_input(
        "🌍 Where do you want to go?",
        placeholder="e.g., Kalavallapalli,Pasivedala,Velivennu,Paris, France or Tokyo, Japan,",
        help="Enter your travel destination"
    )
    
    # Date range input
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "📅 Start Date",
            value=datetime(2025, 12, 24),
            help="When do you want to start your trip?"
        )
    
    with col2:
        end_date = st.date_input(
            "📅 End Date",
            value=datetime(2025, 12, 31),
            help="When does your trip end?"
        )
    
    st.markdown("---")
    
    # Validation
    if start_date >= end_date:
        st.error("❌ End date must be after start date!")
        submit_button = st.button("Generate Itinerary", disabled=True)
    elif not destination.strip():
        st.warning("⚠️ Please enter a destination")
        submit_button = st.button("Generate Itinerary", disabled=True)
    else:
        submit_button = st.button("🚀 Generate Itinerary", use_container_width=True)

# Main content area
if submit_button and destination.strip() and start_date < end_date:
    # Format dates as string
    dates_str = f"{start_date} to {end_date}"
    
    # Show loading message
    with st.spinner(f"✨ Creating an amazing itinerary for {destination}..."):
        try:
            # Call the trip planner function
            itinerary = generate_trip_itinerary(
                destination=destination,
                dates=dates_str,
                thread_id=f"streamlit_{datetime.now().timestamp()}"
            )
            
            # Display the itinerary
            st.success("✅ Itinerary generated successfully!")
            
            st.markdown("---")
            
            # Display trip summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Destination", destination)
            with col2:
                num_days = (end_date - start_date).days
                st.metric("Duration", f"{num_days} days")
            with col3:
                st.metric("Start Date", start_date.strftime("%b %d, %Y"))
            
            st.markdown("---")
            
            # Display itinerary
            st.subheader("📋 Your Travel Itinerary")
            st.markdown(itinerary)
            
            # Download button
            st.download_button(
                label="📥 Download Itinerary as Text",
                data=itinerary,
                file_name=f"itinerary_{destination.replace(', ', '_')}_{start_date}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"❌ Error generating itinerary: {str(e)}")
            st.info("Make sure your API keys are set in the .env file (GROQ_API_KEY and TAVILY_API_KEY)")

else:
    # Default view
    if not submit_button:
        st.info(
            """
            ### 👋 Welcome to AI Trip Planner!
            
            **How it works:**
            1. Enter your destination in the sidebar
            2. Select your travel dates
            3. Click "Generate Itinerary"
            4. Sit back and let AI create your perfect trip plan!
            
            **Features:**
            - 🤖 AI-powered itinerary generation using Groq LLM
            - 🔍 Local event research using Tavily API
            - 📅 Custom date ranges
            - 📥 Download your itinerary
            
            **Requirements:**
            - Groq API Key (GROQ_API_KEY in .env)
            - Tavily API Key (TAVILY_API_KEY in .env)
            """
        )
        
        # Example trips
        st.markdown("---")
        st.subheader("✨ Example Destinations")
        
        example_trips = [
            ("🇫🇷 Paris, France", "Europe's romantic capital"),
            ("🇯🇵 Tokyo, Japan", "Blend of tradition and modernity"),
            ("🇮🇳 Pondicherry, India", "Coastal charm and culture"),
            ("🇲🇽 Mexico City, Mexico", "Rich history and vibrant culture"),
        ]
        
        cols = st.columns(2)
        for idx, (destination_name, description) in enumerate(example_trips):
            with cols[idx % 2]:
                st.markdown(f"**{destination_name}**")
                st.caption(description)
