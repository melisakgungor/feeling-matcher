import streamlit as st
import pandas as pd

st.title("🎧 Feeling Matcher")

df = pd.read_csv("songs.csv")

weights = {
    "Mood": 40,
    "Vibe": 25,
    "Vocals": 15,
    "Beat": 15,
    "Energy": 5
}

song_list = df["Song"] + " - " + df["Artist"]

selected_song = st.selectbox("Pick a song:", song_list)

selected_row = df[song_list == selected_song].iloc[0]

def calculate_score(row):
    score = 0
    reasons = []

    for key in weights:
        if row[key] == selected_row[key]:
            score += weights[key]
            reasons.append(key)

    return score, reasons

results = []

for i, row in df.iterrows():
    if row["Song"] == selected_row["Song"]:
        continue

    score, reasons = calculate_score(row)

    results.append({
        "Song": row["Song"],
        "Artist": row["Artist"],
        "Score": score,
        "Reason": ", ".join(reasons)
    })

results = sorted(results, key=lambda x: x["Score"], reverse=True)

st.subheader("Recommendations")

for r in results[:5]:
    st.write(f"**{r['Song']} - {r['Artist']}**")
    st.write(f"Match: {r['Score']}%")
    st.write(f"Reason: {r['Reason']}")
