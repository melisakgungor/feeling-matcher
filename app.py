import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Feeling Matcher", page_icon="🍀")

st.markdown("""
<h1 style='text-align: center; color: white;'>🍀 For You</h1>
<p style='text-align: center; color: navy;'>songs that feel like you</p>
""", unsafe_allow_html=True)
st.write("Choose a song you already like, or manually add a new song feeling.")

liked = pd.read_csv("liked_songs.csv")
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
    "metal": ["metal", "heavy metal", "classic metal", "thrash metal", "hard rock", "metal ballad"],
    "classic rock": ["classic rock", "blues rock", "soft rock", "folk rock", "prog rock"],
    "new wave": ["new wave", "post punk", "synth pop", "synth rock"],
    "turkish rock": ["turkish rock", "turkish indie", "anatolian rock"]
}

def family_of(beat):
    beat = str(beat).lower()
    for family, styles in rock_families.items():
        if beat in styles:
            return family
    return beat

def car_animation():
    st.markdown("""
    <style>
    .car-container {
        position: fixed;
        bottom: 0;
        left: -100%;
        width: 100%;
        height: 100px;
        background: navy;
        animation: drive 2.5s ease-out forwards;
        z-index: 9999;
    }

    @keyframes drive {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    </style>

    <div class="car-container"></div>
    """, unsafe_allow_html=True)


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

    if c_beat == s_beat or "new wave" in c_beat or "indie" in c_beat:
        score += 35
        reasons.append("same beat style")
    elif family_of(c_beat) == family_of(s_beat):
        score += 22
        reasons.append("same genre family")
    else:
        score -= 10

    if c_mood == s_mood:
        score += 25
        reasons.append("same mood")

    if c_vibe == s_vibe:
        score += 20
        reasons.append("same vibe")
    elif any(word in c_vibe for word in s_vibe.split()):
        score += 10
        reasons.append("similar vibe")

    if c_vocals == s_vocals:
        score += 10
        reasons.append("similar vocals")

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


mode = st.radio("How do you want to choose the song?", ["Select existing song", "Manually add new song"])

selected = None

if mode == "Select existing song":
    song_options = liked["Song"] + " - " + liked["Artist"]
    selected_song = st.selectbox("Choose a song he likes:", song_options)
    selected = liked[(liked["Song"] + " - " + liked["Artist"]) == selected_song].iloc[0]

else:
    song_name = st.text_input("Song name")
    artist_name = st.text_input("Artist")

    mood = st.selectbox("Mood", [
        "melancholic", "dark", "nostalgic", "romantic", "restless",
        "dramatic", "euphoric", "detached", "anxious", "aggressive",
        "dreamy", "fragile", "hopeful", "seductive"
    ])

    energy = st.selectbox("Energy", [
        "low", "low-medium", "medium", "medium-high", "high"
    ])

    vocals = st.selectbox("Vocals", [
        "soft", "raw", "powerful", "distant", "lazy", "smooth",
        "haunting", "emotional", "deep", "dramatic"
    ])

    beat = st.selectbox("Beat / style", [
        "indie rock", "garage rock", "post punk", "dream pop", "shoegaze",
        "alt rock", "classic rock", "hard rock", "heavy metal",
        "thrash metal", "metal ballad", "new wave", "synth pop",
        "turkish indie", "turkish rock", "anatolian rock"
    ])

    lyrics = st.text_input("Lyrics theme", value="unknown")
    vibe = st.text_input("Vibe", value="late night")

    if song_name and artist_name:
        selected = {
            "Song": song_name,
            "Artist": artist_name,
            "Mood": mood,
            "Energy": energy,
            "Vocals": vocals,
            "Beat": beat,
            "Lyrics": lyrics,
            "Vibe": vibe
        }


if selected is not None:
    st.subheader("Song DNA")
    st.write(selected)

    import time

    if random.random() < 0.08:
        popup = st.empty()

        popup.markdown("""
        <div style="
            position:fixed;
            top:20%;
            left:50%;
            transform:translate(-50%, -50%);
            background-color:#1f1f1f;
            padding:20px 30px;
            border-radius:15px;
            text-align:center;
            box-shadow:0 8px 20px rgba(0,0,0,0.5);
            z-index:9999;
            color:white;
        ">
        şarkı lazımdır ağabey?
        </div>
        """, unsafe_allow_html=True)
    
        time.sleep(2)
        popup.empty()

    # long-distance us mode
    couple_mode = st.toggle("✦ us mode")

    if couple_mode:
        st.markdown("""
        <div style="text-align:center; padding:18px; border-radius:15px; background-color:#1f1f1f; margin-bottom:15px;">
        <span style="color:gray;">farklı şehirler, aynı şarkı</span>
        </div>
        """, unsafe_allow_html=True)

    selected_song_name = str(selected["Song"]).lower().strip()
    selected_artist_name = str(selected["Artist"]).lower().strip()

    if selected_song_name == "welcome to japan" and "the strokes" in selected_artist_name:
        st.balloons()
        st.success("you unlocked: Welcome to Japan mode")
        st.markdown("""
        ### Welcome to Japan
        You found the song I secretly built this around :P
    
        *You found the hidden track!*
        """)

        car_songs = [
        "time is running out",
        "selfless",
        "welcome to japan",
        "505",
        "do i wanna know",
    ]

    if selected_song_name in car_songs:
        car_animation()

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
    results_df = results_df[results_df["Score"] >= 35]

    if results_df.empty:
        st.warning("Not enough close matches yet. Add more songs from this style to candidate_songs.csv.")
    else:
        results_df = results_df.sort_values(by="Score", ascending=False)

        top_pool = results_df.head(25)

        results_df = top_pool.sample(
            n=min(10, len(top_pool)),
            random_state=random.randint(1, 999999)
        ).sort_values(by="Score", ascending=False)

        st.subheader("Songs he might discover")

    for _, row in results_df.iterrows():
        st.markdown(f"""
        <div style="
        background-color:#1f1f1f;
        padding:15px;
        border-radius:15px;
        margin-bottom:12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        ">
        
        <h4 style="margin-bottom:5px;">{row['Song']} — {row['Artist']}</h4>
    
        <p style="color:#ff4b4b; margin:0;">Match: {row['Score']}%</p>
        
        <p style="margin:5px 0;">
        {row['Mood']} • {row['Beat']} • {row['Vibe']}
        </p>
    
        <p style="color:gray; font-size:12px;">
        {row['Reason']}
        </p>

        </div>
        """, unsafe_allow_html=True)
