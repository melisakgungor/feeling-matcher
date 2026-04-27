import streamlit as st
import pandas as pd

st.set_page_config(page_title="Feeling Matcher", page_icon="🍀")

st.title("🎧 Feeling Matcher")
st.write("Pick a song he already likes. Discover songs he may not know.")

liked = pd.read_csv("liked_songs.csv")
candidates = pd.read_csv("candidate_songs.csv")

weights = {
    "Mood": 35,
    "Vibe": 25,
    "Vocals": 15,
    "Beat": 15,
    "Energy": 10
}

song_options = liked["Song"] + " - " + liked["Artist"]

selected_song = st.selectbox("Choose a song he likes:", song_options)

selected_row = liked[song_options == selected_song].iloc[0]

st.subheader("Selected Song DNA")
st.write(f"**Mood:** {selected_row['Mood']}")
st.write(f"**Energy:** {selected_row['Energy']}")
st.write(f"**Vocals:** {selected_row['Vocals']}")
st.write(f"**Beat:** {selected_row['Beat']}")
st.write(f"**Vibe:** {selected_row['Vibe']}")

def calculate_match(candidate, selected):
    score = 0
    reasons = []

    for category, weight in weights.items():
        if str(candidate[category]).lower() == str(selected[category]).lower():
            score += weight
            reasons.append(category)

    return score, reasons

results = []

for _, row in candidates.iterrows():
    score, reasons = calculate_match(row, selected_row)

    results.append({
        "Song": row["Song"],
        "Artist": row["Artist"],
        "Score": score,
        "Reason": ", ".join(reasons) if reasons else "different texture, but still near his world",
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
