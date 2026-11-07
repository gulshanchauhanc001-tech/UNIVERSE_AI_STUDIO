
import streamlit as st

st.set_page_config(
    page_title="UNIVERSE AI STUDIO",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #080a12;
    color: #f4f4fa;
}

[data-testid="stSidebar"] {
    background: #101321;
    border-right: 1px solid #25283a;
}

[data-testid="stSidebar"] > div {
    padding-top: 25px;
}

.brand {
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -1px;
    color: white;
    margin-bottom: 4px;
}

.brand span { color: #a78bfa; }

.tagline {
    color: #888da5;
    font-size: 11px;
    letter-spacing: 3px;
    margin-bottom: 30px;
}

.hero {
    background: linear-gradient(115deg, #17152d, #211c40 55%, #151a30);
    border: 1px solid #373052;
    border-radius: 22px;
    padding: 35px;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 37px;
    font-weight: 800;
    margin: 0;
    color: white;
}

.hero p {
    color: #b7b1d2;
    font-size: 14px;
    margin-top: 12px;
}

.eyebrow {
    color: #b69aff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    margin-bottom: 12px;
}

.panel {
    background: #121626;
    border: 1px solid #282d43;
    border-radius: 17px;
    padding: 22px;
    min-height: 135px;
    margin-bottom: 15px;
}

.panel h3 {
    color: white;
    font-size: 17px;
    margin: 8px 0;
}

.panel p {
    color: #9299b2;
    font-size: 12px;
}

.panel-icon { font-size: 27px; }

.section-title {
    color: white;
    font-size: 21px;
    font-weight: 700;
    margin: 25px 0 15px;
}

.metric {
    background: #121626;
    border: 1px solid #282d43;
    padding: 18px;
    border-radius: 15px;
}

.metric small { color: #9299b2; }
.metric h2 { color: white; margin: 7px 0 0; }

.stButton > button {
    background: linear-gradient(90deg, #8058e8, #a06af5);
    color: white;
    border: 0;
    border-radius: 10px;
    padding: 11px 22px;
    font-weight: 700;
    min-height: 43px;
}

.stButton > button:hover {
    background: #b08cff;
    color: white;
    border: 0;
}

.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background: #171c2d;
    color: white;
    border-color: #343950;
    border-radius: 10px;
}

label { color: #c8cbe0 !important; }

hr { border-color: #282d43; }

footer { visibility: hidden; }

[data-testid="stHeader"] {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div class="brand">UNIVERSE <span>AI</span></div>
    <div class="tagline">FILMMAKING STUDIO</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "WORKSPACE",
        [
            "🏠 Dashboard",
            "🎬 Text to Video",
            "🖼️ Image to Video",
            "🧑 Character Studio",
            "🌍 Location Studio",
            "🎙️ Voice & Lip-Sync",
            "📋 Storyboard",
            "✂️ Movie Editor",
            "📁 My Projects"
        ],
        label_visibility="visible"
    )

    st.divider()
    st.markdown("### ⚙️ Settings")
    st.caption("UNIVERSE AI STUDIO")
    st.caption("Version 1.0 • UI Prototype")

# DASHBOARD
if page == "🏠 Dashboard":
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">YOUR CREATIVE UNIVERSE</div>
        <h1>Imagine. Create. <span style="color:#b69aff">Direct.</span></h1>
        <p>Turn your imagination into cinematic stories with AI-powered filmmaking tools.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Your Workspace</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    cards = [
        ("🎬", "Text to Video", "Create cinematic scenes from text prompts."),
        ("🖼️", "Image to Video", "Bring your images to life with motion."),
        ("🧑", "Character Studio", "Create and manage consistent characters."),
        ("🌍", "Location Studio", "Keep locations consistent across scenes."),
        ("🎙️", "Voice & Lip-Sync", "Dialogue, emotion and character voices."),
        ("📋", "Storyboard", "Plan your film scene by scene.")
    ]

    for i, (icon, title, desc) in enumerate(cards):
        with [c1, c2, c3][i % 3]:
            st.markdown(f"""
            <div class="panel">
                <div class="panel-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Studio Overview</div>',
                unsafe_allow_html=True)

    a, b, c = st.columns(3)
    for col, number, label in [
        (a, "00", "Projects"),
        (b, "00", "Scenes"),
        (c, "00", "Characters")
    ]:
        with col:
            st.markdown(f"""
            <div class="metric">
                <small>{label}</small>
                <h2>{number}</h2>
            </div>
            """, unsafe_allow_html=True)

# TEXT TO VIDEO
elif page == "🎬 Text to Video":
    st.markdown("## 🎬 Text to Video")
    st.caption("Create a cinematic scene from your imagination.")

    prompt = st.text_area(
        "Describe your scene",
        placeholder="A cinematic shot of a mysterious warrior walking through an ancient city at night...",
        height=160
    )

    a, b, c = st.columns(3)
    with a:
        style = st.selectbox("Visual Style", [
            "Cinematic", "Anime", "Realistic", "Fantasy",
            "Sci-Fi", "Horror", "3D Animation"
        ])
    with b:
        ratio = st.selectbox("Aspect Ratio", [
            "16:9", "9:16", "1:1"
        ])
    with c:
        duration = st.selectbox("Duration", [
            "5 seconds", "10 seconds", "15 seconds",
            "30 seconds"
        ])

    if st.button("✨ Prepare Video Prompt"):
        if prompt.strip():
            st.success("Your prompt is ready!")
            st.code(prompt)
            st.info("Video generation engine is not connected yet. This prototype prepares your creative settings.")
        else:
            st.warning("Please enter a scene description.")

# IMAGE TO VIDEO
elif page == "🖼️ Image to Video":
    st.markdown("## 🖼️ Image to Video")
    st.caption("Transform a still image into a moving cinematic scene.")

    uploaded = st.file_uploader(
        "Upload your reference image",
        type=["png", "jpg", "jpeg", "webp"]
    )

    if uploaded:
        st.image(uploaded, width=450)

    motion = st.text_area(
        "Describe the movement",
        placeholder="Camera slowly moves forward. Character turns around. Wind moves the hair..."
    )

    if st.button("✨ Prepare Animation"):
        if uploaded and motion.strip():
            st.success("Image and motion prompt are ready.")
            st.info("Connect a supported video engine to generate the actual clip.")
        else:
            st.warning("Upload an image and describe its movement.")

# CHARACTER STUDIO
elif page == "🧑 Character Studio":
    st.markdown("## 🧑 Character Studio")
    st.caption("Build your character reference library.")

    image = st.file_uploader(
        "Upload character reference",
        type=["png", "jpg", "jpeg", "webp"]
    )

    name = st.text_input("Character Name")
    description = st.text_area(
        "Character Appearance",
        placeholder="Face, hairstyle, clothes, body, accessories, age appearance..."
    )

    if image:
        st.image(image, width=300)

    if st.button("Save Character Profile"):
        if name.strip() and description.strip() and image:
            st.success("Character details prepared for your project.")
            st.info("Persistent character saving will be added in the next development phase.")
        else:
            st.warning("Add a name, appearance description and reference image.")

# LOCATION STUDIO
elif page == "🌍 Location Studio":
    st.markdown("## 🌍 Location Studio")
    st.caption("Create reusable environment references.")

    image = st.file_uploader(
        "Upload location reference",
        type=["png", "jpg", "jpeg", "webp"]
    )

    name = st.text_input("Location Name")
    details = st.text_area(
        "Describe the Environment",
        placeholder="Architecture, lighting, weather, colors, objects, camera viewpoint..."
    )

    if image:
        st.image(image, width=400)

    if st.button("Save Location"):
        if name.strip() and details.strip() and image:
            st.success("Location reference details prepared.")
            st.info("Persistent location saving will be added in a later phase.")
        else:
            st.warning("Complete the location details and upload an image.")

# VOICE AND LIP SYNC
elif page == "🎙️ Voice & Lip-Sync":
    st.markdown("## 🎙️ Voice & Lip-Sync")

    character = st.text_input("Character Name")
    dialogue = st.text_area(
        "Dialogue",
        placeholder="Enter your Hindi or English dialogue here..."
    )

    a, b = st.columns(2)
    with a:
        language = st.selectbox("Language", [
            "Hindi", "English", "Hinglish"
        ])
    with b:
        emotion = st.selectbox("Emotion", [
            "Natural", "Happy", "Sad", "Angry",
            "Fearful", "Excited", "Whispering"
        ])

    if st.button("Prepare Voice Scene"):
        if dialogue.strip():
            st.success("Dialogue settings prepared.")
            st.write("Character:", character or "Not specified")
            st.write("Language:", language)
            st.write("Emotion:", emotion)
            st.info("Voice generation and lip-sync engines are not connected yet.")
        else:
            st.warning("Enter dialogue first.")

# STORYBOARD
elif page == "📋 Storyboard":
    st.markdown("## 📋 Storyboard")
    st.caption("Plan your film scene by scene.")

    if "scenes" not in st.session_state:
        st.session_state.scenes = []

    with st.form("scene_form"):
        scene_name = st.text_input("Scene Name")
        scene_prompt = st.text_area("Scene Description")
        camera = st.selectbox("Camera Movement", [
            "Static", "Pan", "Tilt", "Zoom In",
            "Zoom Out", "Tracking", "Drone Shot"
        ])
        submitted = st.form_submit_button("＋ Add Scene")

        if submitted:
            if scene_name.strip() and scene_prompt.strip():
                st.session_state.scenes.append({
                    "name": scene_name,
                    "prompt": scene_prompt,
                    "camera": camera
                })
                st.success("Scene added to storyboard.")
            else:
                st.warning("Enter scene name and description.")

    st.divider()
    for i, scene in enumerate(st.session_state.scenes):
        with st.expander(f"Scene {i+1}: {scene['name']}"):
            st.write(scene["prompt"])
            st.caption("Camera: " + scene["camera"])

    if st.button("Clear Storyboard"):
        st.session_state.scenes = []
        st.rerun()

# MOVIE EDITOR
elif page == "✂️ Movie Editor":
    st.markdown("## ✂️ Movie Editor")
    st.caption("Prepare your clips and final film.")

    clips = st.file_uploader(
        "Upload video clips",
        type=["mp4", "mov", "webm"],
        accept_multiple_files=True
    )

    if clips:
        st.success(f"{len(clips)} clip(s) uploaded.")
        for clip in clips:
            st.write("🎞️", clip.name)

    music = st.file_uploader(
        "Upload background music",
        type=["mp3", "wav"]
    )

    if music:
        st.write("🎵", music.name)

    st.info("Timeline editing, transitions, subtitles and MP4 rendering will be developed in the editing phase.")

# PROJECTS
elif page == "📁 My Projects":
    st.markdown("## 📁 My Projects")
    st.caption("Your filmmaking workspace.")

    if "scenes" not in st.session_state:
        st.session_state.scenes = []

    st.metric("Storyboard Scenes", len(st.session_state.scenes))

    if st.session_state.scenes:
        for i, scene in enumerate(st.session_state.scenes):
            st.write(f"**{i+1}. {scene['name']}**")
            st.caption(scene["prompt"])
    else:
        st.info("No scenes created yet. Start with Storyboard.")

st.divider()
st.markdown(
    "<center style='color:#666d86;font-size:11px'>"
    "UNIVERSE AI STUDIO • CREATE YOUR OWN UNIVERSE"
    "</center>",
    unsafe_allow_html=True
)
