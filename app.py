import streamlit as st
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="Feeling Matcher", page_icon="🍀")

st.title("Feeling Matcher")
st.write("Type a song you like. The app finds new songs with the same feeling;)")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

candidates = pd.read_csv("candidate_songs.csv")

weights = {
    "Mood": 35,
    "Vibe": 25,
    "Vocals": 15,
    "Beat": 15,
    "Energy": 10
}

song_name = st.text_input("Song name")
artist_name = st.text_input("Artist")

@st.cache_data
def analyze_song(song, artist):
    prompt = f"""
Analyze this song for a music discovery app.

Song: {song}
Artist: {artist}

Return ONLY a CSV row with:
Song,Artist,Mood,Energy,Vocals,Beat,Lyrics,Vibe

Example:
Selfless,The Strokes,melancholic,medium,distant,indie rock,emotional distance,late night city
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-nano",
            input=prompt
        )

        text = response.output_text.strip()
        values = [v.strip() for v in text.split(",")]

        if len(values) != 8:
            raise ValueError("Bad format")

        return {
            "Song": values[0],
            "Artist": values[1],
            "Mood": values[2],
            "Energy": values[3],
            "Vocals": values[4],
            "Beat": values[5],
            "Lyrics": values[6],
            "Vibe": values[7]
        }

    except Exception:
        return {
            "Song": song,
            "Artist": artist,
            "Mood": "melancholic",
            "Energy": "medium",
            "Vocals": "soft",
            "Beat": "indie rock",
            "Lyrics": "unknown",
            "Vibe": "late night"
        }
     

def calculate_match(candidate, selected):
    score = 0
    reasons = []

    for category, weight in weights.items():
        if str(candidate[category]).lower() == str(selected[category]).lower():
            score += weight
            reasons.append(category)

    return score, reasons

if st.button("Find songs"):
    if not song_name or not artist_name:
        st.warning("Write both song and artist.")
    else:
        selected = analyze_song(song_name, artist_name)

        st.subheader("Song DNA")
        st.write(selected)

        results = []

        for _, row in candidates.iterrows():
            score, reasons = calculate_match(row, selected)

            results.append({
                "Song": row["Song"],
                "Artist": row["Artist"],
                "Score": score,
                "Reason": ", ".join(reasons) if reasons else "different texture, but still nearby",
                "Mood": row["Mood"],
                "Vibe": row["Vibe"]
            })

        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values(by="Score", ascending=False)

        st.subheader("Songs he might discover")

        for _, row in results_df.head(10).iterrows():
            st.markdown(f"### {row['Song']} - {row['Artist']}")
            st.write(f"**Match:** {row['Score']}%")
            st.write(f"**Why:** same {row['Reason']}")
            st.write(f"**Mood:** {row['Mood']} | **Vibe:** {row['Vibe']}")
            st.divider()
