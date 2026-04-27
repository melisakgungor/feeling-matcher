import streamlit as st
import pandas as pd
from openai import OpenAI
import json
import random

st.set_page_config(page_title="Feeling Matcher", page_icon="🎧")

st.title("Feeling Matcher For Arda")
st.write("Type a song you like let the app match it.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

candidates = pd.read_csv("candidate_songs.csv")

energy_rank = {
    "low": 1,
    "low-medium": 2,
    "medium": 3,
    "medium-high": 4,
    "high": 5
}

rock_families = {
    "indie rock": ["indie rock", "garage rock", "post punk", "dream pop", "shoegaze", "alt rock"],
    "metal": ["metal", "heavy metal", "classic metal", "thrash metal", "hard rock"],
    "classic rock": ["classic rock", "blues rock", "soft rock", "folk rock", "prog rock"],
    "new wave": ["new wave", "post punk", "synth pop", "synth rock"],
    "turkish rock": ["turkish rock", "turkish indie", "anatolian rock"]
}

@st.cache_data
def analyze_song(song, artist):
    prompt = f"""
Analyze this song for a music recommendation app.

Song: {song}
Artist: {artist}

Return ONLY valid JSON in this exact structure:

{{
  "Song": "",
  "Artist": "",
  "Mood": "",
  "Energy": "",
  "Vocals": "",
  "Beat": "",
  "Lyrics": "",
  "Vibe": ""
}}

Rules:
- Energy must be one of: low, low-medium, medium, medium-high, high
- Beat must be specific, not vague.
Examples: indie rock, garage rock, post punk, dream pop, shoegaze, alt rock, classic rock, hard rock, heavy metal, thrash metal, metal ballad, new wave, synth pop, turkish indie, turkish rock
- Mood should be specific: melancholic, detached, dark, restless, romantic, nostalgic, aggressive, anxious, dramatic, euphoric
- Vibe should be emotional and short: night drive, city tension, storm energy, cigarette balcony, empty room, chaotic attraction, late night spiral
- Do not classify metal songs as indie rock.
"""

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt
    )

    text = response.output_text.strip()

    try:
        return json.loads(text)
    except Exception:
        st.error("AI gave a messy answer. Try again.")
        st.stop()


def family_of(beat):
    beat = str(beat).lower()
    for family, styles in rock_families.items():
        if beat in styles:
            return family
    return beat


def calculate_match(candidate, selected):
    score = 0
    reasons = []

    c_mood = str(candidate["Mood"]).lower()
    s_mood = str(selected["Mood"]).lower()

    c_vibe = str(candidate["Vibe"]).lower()
    s_vibe = str(selected["Vibe"]).lower()

    c_vocals = str(candidate["Vocals"]).lower()
    s_vocals = str(selected["Vocals"]).lower()

    c_beat = str(candidate["Beat"]).lower()
    s_beat = str(selected["Beat"]).lower()

    c_energy = str(candidate["Energy"]).lower()
    s_energy = str(selected["Energy"]).lower()

    # Beat / genre family is now VERY important
    if c_beat == s_beat:
        score += 35
        reasons.append("same beat style")
    elif family_of(c_beat) == family_of(s_beat):
        score += 22
        reasons.append("same genre family")
    else:
        score -= 20

    # Mood
    if c_mood == s_mood:
        score += 25
        reasons.append("same mood")

    # Vibe
    if c_vibe == s_vibe:
        score += 20
        reasons.append("same vibe")
    elif any(word in c_vibe for word in s_vibe.split()):
        score += 10
        reasons.append("similar vibe")

    # Vocals
    if c_vocals == s_vocals:
        score += 10
        reasons.append("similar vocals")

    # Energy distance
    c_e = energy_rank.get(c_energy, 3)
    s_e = energy_rank.get(s_energy, 3)
    distance = abs(c_e - s_e)

    if distance == 0:
        score += 10
        reasons.append("same energy")
    elif distance == 1:
        score += 5
        reasons.append("close energy")
    else:
        score -= 10

    return max(score, 0), reasons


song_name = st.text_input("Song name")
artist_name = st.text_input("Artist")

if st.button("Find songs"):
    if not song_name or not artist_name:
        st.warning("Write both song and artist.")
    else:
        selected = analyze_song(song_name, artist_name)

        st.subheader("Song DNA")
        st.json(selected)

        results = []

        for _, row in candidates.iterrows():
            score, reasons = calculate_match(row, selected)

            results.append({
                "Song": row["Song"],
                "Artist": row["Artist"],
                "Score": score,
                "Reason": ", ".join(reasons) if reasons else "different texture",
                "Mood": row["Mood"],
                "Beat": row["Beat"],
                "Vibe": row["Vibe"]
            })

        results_df = pd.DataFrame(results)

        # Only keep decent matches
        results_df = results_df[results_df["Score"] >= 35]

        if results_df.empty:
            st.warning("Not enough close matches in your dataset yet. Add more songs from this genre.")
        else:
            # Avoid same top songs every time
            results_df = results_df.sort_values(by="Score", ascending=False)
            top_pool = results_df.head(25)
            results_df = top_pool.sample(
                n=min(10, len(top_pool)),
                random_state=random.randint(1, 999999)
            ).sort_values(by="Score", ascending=False)

            st.subheader("Songs he might discover")

            for _, row in results_df.iterrows():
                st.markdown(f"### {row['Song']} - {row['Artist']}")
                st.write(f"**Match:** {row['Score']}%")
                st.write(f"**Why:** {row['Reason']}")
                st.write(f"**Mood:** {row['Mood']} | **Beat:** {row['Beat']} | **Vibe:** {row['Vibe']}")
                st.divider()
