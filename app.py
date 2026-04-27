import streamlit as st
import pandas as pd
from openai import OpenAI

st.title("Feeling Matcher")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

df = pd.read_csv("songs.csv")

weights = {
    "Mood": 40,
    "Vibe": 25,
    "Vocals": 15,
    "Beat": 15,
    "Energy": 5
}

song_name = st.text_input("Write a song you like:")
artist_name = st.text_input("Artist:")

def ai_categorize(song, artist):
    prompt = f"""
Categorize this song for a music recommendation app.

Song: {song}
Artist: {artist}

Return ONLY this format:
Mood:
Energy:
Vocals:
Beat:
Lyrics:
Vibe:
"""

    response = client.responses.create(
        model="gpt-5.1-mini",
        input=prompt
    )

    return response.output_text

if st.button("Analyze song"):
    if song_name and artist_name:
        analysis = ai_categorize(song_name, artist_name)
        st.subheader("AI Song DNA")
        st.text(analysis)
    else:
        st.warning("Write both song and artist.")
