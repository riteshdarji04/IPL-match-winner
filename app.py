import streamlit as st
import pandas as pd
import pickle
import base64
import os

# Load model
pipe = pickle.load(open('pipe.pkl', 'rb'))

# Team and city info
teams = [
    'Chennai Super Kings', 'Delhi Capitals', 'Kings XI Punjab',
    'Kolkata Knight Riders', 'Mumbai Indians',
    'Rajasthan Royals', 'Royal Challengers Bangalore',
    'Sunrisers Hyderabad'
]

cities = ['Mumbai', 'Kolkata', 'Delhi', 'Chennai', 'Hyderabad', 'Jaipur', 'Bangalore', 'Ahmedabad', 'Pune', 'Nagpur']

# Apply Background CSS
def set_bg_image(image_file):
    with open(image_file, "rb") as img:
        img_bytes = base64.b64encode(img.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{img_bytes}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# set_bg_image("background.jpg")

# Streamlit title and logo
st.markdown("<h1 style='text-align: center; color: white;'>🏏 IPL Match Winner Predictor</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: white;'>Predict the outcome of an IPL match's second innings</h4>", unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.title("Enter Match Details")

batting_team = st.sidebar.selectbox('Batting Team', teams)
bowling_team = st.sidebar.selectbox('Bowling Team', [team for team in teams if team != batting_team])
city = st.sidebar.selectbox('Match City', cities)

target = st.sidebar.number_input('Target Score', min_value=1)
score = st.sidebar.number_input('Current Score', min_value=0, max_value=target)
overs = st.sidebar.number_input('Overs Completed', min_value=0, max_value=20, step=1)
wickets = st.sidebar.number_input('Wickets Lost', min_value=0, max_value=10)

# Team logos
col1, col2 = st.columns(2)
with col1:
    st.image(f"team_logos/{batting_team}.png", width=150, caption=f"Batting: {batting_team}")
with col2:
    st.image(f"team_logos/{bowling_team}.png", width=150, caption=f"Bowling: {bowling_team}")

# Predict Button
if st.button("Predict Match Result"):

    try:
        balls_left = 120 - int(overs * 6)
        runs_left = target - score
        wickets_left = 10 - wickets
        crr = score / overs if overs > 0 else 0
        rrr = (runs_left * 6 / balls_left) if balls_left > 0 else 0

        input_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'city': [city],
            'runs_left': [runs_left],
            'balls_left': [balls_left],
            'wickets_left': [wickets_left],
            'total_runs_x': [target],
            'crr': [crr],
            'rrr': [rrr]
        })

        result = pipe.predict(input_df)[0]
        prob = pipe.predict_proba(input_df)[0][1]

        # Display result
        st.markdown("---")
        st.subheader("📊 Prediction Insights:")

        if result == 1:
            st.success(f"✅ {batting_team} is likely to WIN the match!")
        else:
            st.error(f"❌ {batting_team} is likely to LOSE the match.")

        st.metric(label="🎯 Win Probability", value=f"{prob*100:.2f}%")
        st.progress(min(int(prob*100), 100))

    except Exception as e:
        st.warning("⚠️ Please fill all fields correctly.")
        st.text(f"Error: {e}")
