
import streamlit as st
import json
import re
import sqlite3
import secrets as py_secrets
import extra_streamlit_components as stx
from datetime import datetime, timedelta
from supabase_auth import SyncSupportedStorage
from supabase import create_client
from supabase.client import ClientOptions

# -----------------------------------------
# APP CONFIG
# -----------------------------------------

st.set_page_config(
    page_title="UNIVERSE AI STUDIO",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------------------
# SUPABASE
# -----------------------------------------

# -----------------------------------------
# PKCE STORAGE
# -----------------------------------------

class StreamlitSQLiteStorage(SyncSupportedStorage):

    def __init__(self, namespace):
        self.namespace = namespace
        self.db_path = "/tmp/universe_ai_auth.sqlite3"

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS auth_storage (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

    def _key(self, key):
        return f"{self.namespace}:{key}"

    def get_item(self, key):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value FROM auth_storage WHERE key = ?",
                (self._key(key),)
            ).fetchone()

        return row[0] if row else None

    def set_item(self, key, value):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO auth_storage (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (self._key(key), value))

    def remove_item(self, key):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM auth_storage WHERE key = ?",
                (self._key(key),)
            )


# -----------------------------------------
# PERSISTENT BROWSER SESSION ID
# -----------------------------------------

cookie_manager = stx.CookieManager(key="universe_auth_cookies")

AUTH_COOKIE_NAME = "universe_auth_sid"

query_namespace = st.query_params.get("auth_sid")
cookie_namespace = cookie_manager.get(AUTH_COOKIE_NAME)

AUTH_NAMESPACE = query_namespace or cookie_namespace

if not AUTH_NAMESPACE:
    AUTH_NAMESPACE = py_secrets.token_urlsafe(32)

    cookie_manager.set(
        AUTH_COOKIE_NAME,
        AUTH_NAMESPACE,
        expires_at=datetime.now() + timedelta(days=30)
    )

    st.info("Login session prepare ho raha hai. Ek pal wait karo.")
    st.stop()

if cookie_namespace != AUTH_NAMESPACE:
    cookie_manager.set(
        AUTH_COOKIE_NAME,
        AUTH_NAMESPACE,
        expires_at=datetime.now() + timedelta(days=30)
    )


# -----------------------------------------
# SUPABASE
# -----------------------------------------

def get_supabase():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["anon_key"],
        options=ClientOptions(
            flow_type="pkce",
            storage=StreamlitSQLiteStorage(AUTH_NAMESPACE)
        )
    )


def redirect_url():
    base = st.secrets["supabase"]["redirect_url"].rstrip("/")
    return f"{base}/?auth_sid={AUTH_NAMESPACE}"


def set_logged_in_user(user, method):
    st.session_state.logged_in = True
    st.session_state.username = getattr(user, "email", "") or ""
    st.session_state.user_id = str(user.id)

    metadata = getattr(user, "user_metadata", None) or {}

    st.session_state.profile_name = (
        metadata.get("full_name")
        or metadata.get("name")
        or metadata.get("display_name")
        or ""
    )

    st.session_state.auth_method = method


# -----------------------------------------
# AI BRAIN - LONG TERM MEMORY
# -----------------------------------------

def save_ai_memory(project_name, memory_type, title, content):
    user_id = st.session_state.get("user_id")

    if not user_id:
        return False, "User login required."

    try:
        response = get_supabase().table("ai_memory").insert({
            "user_id": user_id,
            "project_name": project_name,
            "memory_type": memory_type,
            "title": title,
            "content": content
        }).execute()

        return True, "Memory saved successfully."

    except Exception as e:
        return False, str(e)


def load_ai_memories(project_name):
    user_id = st.session_state.get("user_id")

    if not user_id:
        return []

    try:
        response = (
            get_supabase()
            .table("ai_memory")
            .select("*")
            .eq("user_id", user_id)
            .eq("project_name", project_name)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as e:
        st.error(f"Memory loading error: {e}")
        return []


# -----------------------------------------
# SESSION DATA
# -----------------------------------------

defaults = {
    "logged_in": False,
    "username": "",
    "user_id": None,
    "profile_name": "",
    "auth_method": "",
    "otp_email": "",
    "otp_sent": False,
    "scenes": [],
    "characters": [],
    "locations": [],
    "projects": [],
    "clips": [],
    "project_name": "My First Film",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------------------
# DESIGN
# -----------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    color-scheme: dark;
    --bg: #080b14;
    --surface: rgba(17, 23, 39, .88);
    --surface-2: #151d30;
    --line: rgba(148, 163, 184, .16);
    --text: #f4f6ff;
    --muted: #9aa6bd;
    --accent: #9b87ff;
    --accent-2: #63d5c6;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

.stApp {
    background:
        radial-gradient(ellipse at 12% 0%, rgba(105, 75, 190, .22), transparent 34%),
        radial-gradient(ellipse at 92% 8%, rgba(42, 117, 153, .16), transparent 30%),
        linear-gradient(145deg, #080b14 0%, #0b1020 52%, #090d18 100%);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: rgba(8, 11, 20, .72);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101629 0%, #0c1221 100%);
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.4rem;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    font-family: 'Manrope', sans-serif;
    letter-spacing: -.035em;
    color: #f7f8ff;
}

h1 { font-weight: 800; }
h2, h3 { font-weight: 700; }

.brand {
    font-family: 'Manrope', sans-serif;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -.06em;
    color: #fff;
}

.brand span {
    color: var(--accent);
}

.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(120deg, rgba(42, 34, 76, .96), rgba(23, 34, 61, .94) 58%, rgba(17, 48, 62, .9));
    border: 1px solid rgba(167, 139, 250, .24);
    border-radius: 22px;
    padding: 30px 32px;
    margin-bottom: 24px;
    box-shadow: 0 18px 55px rgba(0, 0, 0, .2);
}

.hero:after {
    content: "";
    position: absolute;
    width: 230px;
    height: 230px;
    right: -90px;
    top: -130px;
    border-radius: 50%;
    background: rgba(158, 139, 255, .14);
    filter: blur(4px);
    pointer-events: none;
}

.hero p, .small-muted {
    color: #b8bfd2;
}

.small-muted {
    font-size: 13px;
}

.panel {
    background: linear-gradient(145deg, rgba(24, 32, 53, .96), rgba(17, 24, 41, .96));
    border: 1px solid var(--line);
    border-radius: 17px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, .12);
}

.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
    min-height: 42px;
    border: 1px solid rgba(179, 162, 255, .22);
    border-radius: 11px;
    color: #fff;
    background: linear-gradient(105deg, #7057dc 0%, #8e6ce9 55%, #657ce7 100%);
    font-weight: 700;
    transition: transform .16s ease, filter .16s ease, box-shadow .16s ease;
    box-shadow: 0 7px 20px rgba(106, 83, 211, .18);
}

.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
    filter: brightness(1.09);
    transform: translateY(-1px);
    border-color: rgba(205, 192, 255, .48);
    color: #fff;
    box-shadow: 0 10px 26px rgba(106, 83, 211, .25);
}

.stTextInput input, .stTextArea textarea,
[data-baseweb="select"] > div {
    background: #111a2c;
    color: #f4f6ff;
    border-color: rgba(148, 163, 184, .22);
    border-radius: 10px;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(155, 135, 255, .8);
    box-shadow: 0 0 0 1px rgba(155, 135, 255, .3);
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(25, 34, 56, .95), rgba(17, 24, 41, .95));
    border: 1px solid var(--line);
    padding: 16px 17px;
    border-radius: 15px;
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
}

[data-testid="stMetricValue"] {
    color: #f7f8ff;
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
}

[data-testid="stExpander"] {
    background: rgba(18, 26, 44, .7);
    border: 1px solid var(--line);
    border-radius: 13px;
    overflow: hidden;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 7px;
    border-bottom: 1px solid var(--line);
}

[data-testid="stTabs"] button[role="tab"] {
    border-radius: 9px 9px 0 0;
    padding: 10px 14px;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: #c9bdff;
    border-bottom-color: var(--accent);
}

[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid var(--line);
}

hr, [data-testid="stDivider"] {
    border-color: var(--line);
}

[data-testid="stFileUploader"] {
    background: rgba(17, 26, 44, .58);
    border: 1px dashed rgba(155, 135, 255, .35);
    border-radius: 14px;
    padding: 8px;
}

[data-testid="stSidebar"] .stRadio label {
    color: #d8def0;
}

footer { visibility: hidden; }

@media (max-width: 768px) {
    .block-container {
        padding: 1.1rem 1rem 2.5rem;
    }
    .hero {
        padding: 22px 20px;
        border-radius: 17px;
    }
    .brand {
        font-size: 22px;
    }
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------
# AUTH SCREEN
# -----------------------------------------

def auth_screen():

    st.markdown("<br><br>", unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.4, 1])

    with center:

        st.markdown("""
        <div style="text-align:center">
            <div class="brand">UNIVERSE <span>AI</span></div>
            <p style="letter-spacing:3px;color:#999">
                THE AI FILMMAKING UNIVERSE
            </p>
            <h1>Your Story.<br>Your Universe.</h1>
            <p>Create cinematic worlds with AI.</p>
        </div>
        """, unsafe_allow_html=True)

        email_tab, google_tab = st.tabs([
            "EMAIL LOGIN",
            "GOOGLE LOGIN"
        ])

        with email_tab:

            st.markdown("### Sign in or create account")

            if not st.session_state.otp_sent:

                with st.form("send_otp"):

                    email = st.text_input(
                        "Email Address",
                        placeholder="you@example.com"
                    ).strip().lower()

                    send = st.form_submit_button(
                        "Send OTP",
                        use_container_width=True
                    )

                if send:

                    if "@" not in email:
                        st.error("Valid email enter karo.")

                    else:
                        try:
                            get_supabase().auth.sign_in_with_otp({
                                "email": email,
                                "options": {"should_create_user": True}
                            })

                            st.session_state.otp_email = email
                            st.session_state.otp_sent = True

                            st.success("Email bhej di gayi.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"OTP error: {e}")

            else:

                st.info(
                    f"OTP sent to {st.session_state.otp_email}"
                )

                with st.form("verify_otp"):

                    token = st.text_input(
                        "6-digit OTP",
                        max_chars=6
                    ).strip()

                    verify = st.form_submit_button(
                        "Verify OTP & Login",
                        use_container_width=True
                    )

                if verify:

                    try:

                        if len(token) != 6 or not token.isdigit():
                            st.error("6-digit OTP enter karo.")

                        else:

                            result = get_supabase().auth.verify_otp({
                                "email": st.session_state.otp_email,
                                "token": token,
                                "type": "email"
                            })

                            set_logged_in_user(
                                result.user,
                                "Email OTP"
                            )

                            st.session_state.otp_sent = False
                            st.rerun()

                    except Exception as e:
                        st.error(f"Verification failed: {e}")

                if st.button("Change Email"):
                    st.session_state.otp_sent = False
                    st.rerun()

        with google_tab:

            st.markdown("### Continue with Google")
            st.write("Redirect URL:", redirect_url())

            if st.button(
                "Continue with Google",
                use_container_width=True
            ):

                try:

                    result = get_supabase().auth.sign_in_with_oauth({
                        "provider": "google",
                        "options": {"redirect_to": redirect_url()}
                    })

                    st.link_button(
                        "Open Google Sign In",
                        result.url,
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"Google login error: {e}")

        st.markdown(
            "<p style='text-align:center;color:#888'>"
            "UNIVERSE AI STUDIO • CREATE WITHOUT LIMITS</p>",
            unsafe_allow_html=True
        )


# -----------------------------------------
# GOOGLE CALLBACK
# -----------------------------------------

def handle_google_callback():

    code = st.query_params.get("code")

    if code:
        try:
            result = get_supabase().auth.exchange_code_for_session({
                "auth_code": code
            })

            set_logged_in_user(result.user, "Google")

            st.query_params.clear()
            st.query_params["auth_sid"] = AUTH_NAMESPACE

            st.rerun()

        except Exception as e:
            st.error(f"Google login error: {e}")



# -----------------------------------------
# RESTORE LOGIN SESSION
# -----------------------------------------

if not st.session_state.get("logged_in", False):

    try:
        supabase = get_supabase()
        session = supabase.auth.get_session()

        if session and session.user:
            set_logged_in_user(
                session.user,
                "Restored Session"
            )

    except Exception as e:
        st.warning(f"Session restore error: {e}")


# -----------------------------------------
# LOGIN CHECK
# -----------------------------------------

if not st.session_state.get("logged_in", False):
    handle_google_callback()

if not st.session_state.get("logged_in", False):
    auth_screen()
    st.stop()


# -----------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------

with st.sidebar:

    st.markdown(
        '<div class="brand">UNIVERSE <span>AI</span></div>',
        unsafe_allow_html=True
    )

    st.caption("AI FILMMAKING WORKSPACE")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Overview",
            "🎥 Film Studio",
            "🧩 My Templates",
            "🧑 Character Library",
            "🌍 Location Library",
            "🗂️ Asset Library",
            "📁 My Projects",
            "👤 My Profile",
            "⚙️ Settings"
        ],
        key="main_navigation"
    )

    st.divider()

    st.write(
        "👤",
        st.session_state.profile_name or "Your Profile"
    )

    st.caption(st.session_state.username)
    st.caption(st.session_state.auth_method)

    if st.button("Logout", use_container_width=True):

        try:
            get_supabase().auth.sign_out()
        except Exception:
            pass

        for key in [
            "logged_in",
            "username",
            "profile_name",
            "auth_method",
            "user_id"
        ]:
            st.session_state[key] = (
                False if key == "logged_in"
                else None if key == "user_id"
                else ""
            )

        st.rerun()


# -----------------------------------------
# OVERVIEW - AI BRAIN DASHBOARD
# -----------------------------------------

if page == "🏠 Overview":

    st.markdown("""
    <div class="hero">
        <h1>UNIVERSE AI BRAIN 🧠</h1>
        <p>Your intelligent filmmaking memory workspace.</p>
        <p class="small-muted">
            Your saved creative world, all in one place.
        </p>
    </div>
    """, unsafe_allow_html=True)

    welcome = (
        st.session_state.profile_name
        or st.session_state.username
    )

    st.markdown(f"### Welcome {welcome} 👋")

    brain_project = (
        st.session_state.get("project_name")
        or "My First Film"
    )

    st.markdown(f"### 📁 Current Project: {brain_project}")

    # Load permanent memories from Supabase
    brain_memories = load_ai_memories(brain_project)

    memory_groups = {
        "story": [],
        "character": [],
        "location": [],
        "scene": [],
        "dialogue": [],
        "other": []
    }

    for memory in brain_memories:
        memory_type = memory.get("memory_type", "other")

        if memory_type in memory_groups:
            memory_groups[memory_type].append(memory)
        else:
            memory_groups["other"].append(memory)

    # Memory statistics
    a, b, c, d, e = st.columns(5)

    a.metric("Stories", len(memory_groups["story"]))
    b.metric("Characters", len(memory_groups["character"]))
    c.metric("Locations", len(memory_groups["location"]))
    d.metric("Scenes", len(memory_groups["scene"]))
    e.metric("Dialogues", len(memory_groups["dialogue"]))

    st.markdown("---")
    st.markdown("## 🧠 AI Brain - Saved Memories")

    if not brain_memories:

        st.info(
            "Abhi is project mein koi permanent memory save nahi hai. "
            "Film Studio mein scenes aur dialogues save karo."
        )

    else:

        memory_tabs = st.tabs([
            "📖 Stories",
            "🧑 Characters",
            "🌍 Locations",
            "🎬 Scenes",
            "🎙️ Dialogues",
            "📦 Other"
        ])

        tab_types = [
            "story",
            "character",
            "location",
            "scene",
            "dialogue",
            "other"
        ]

        for memory_tab, memory_type in zip(memory_tabs, tab_types):

            with memory_tab:

                items = memory_groups[memory_type]

                if not items:
                    st.info("Is category mein abhi koi memory nahi hai.")

                for i, memory in enumerate(items):

                    content = memory.get("content") or {}

                    with st.expander(
                        memory.get("title") or f"{memory_type.title()} {i+1}"
                    ):

                        if isinstance(content, dict):

                            for key, value in content.items():

                                if key != "_memory_id":
                                    st.write(
                                        f"**{key.replace('_', ' ').title()}:**",
                                        value
                                    )

                        else:
                            st.write(content)

                        st.caption(
                            f"Saved: {memory.get('created_at', 'Date unavailable')}"
                        )

    st.markdown("---")
    st.markdown("## 🎬 Your Creative Workspace")

    cols = st.columns(3)

    cards = [
        ("🎥 Film Studio", "Create and plan cinematic scenes."),
        ("🧑 Characters", "Create and manage film characters."),
        ("🌍 Locations", "Build your story environments."),
        ("📋 Storyboard", "Organize your film scenes."),
        ("🎙️ Audio", "Prepare dialogue and voice instructions."),
        ("✂️ Editor", "Organize your video clips.")
    ]

    for i, (title, desc) in enumerate(cards):

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="panel">
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# -----------------------------------------
# FILM STUDIO
# -----------------------------------------


elif page == "🎥 Film Studio":

    st.markdown("""
    <div class="hero">
        <h1>🎥 Film Studio</h1>
        <p>Create your scenes and plan your movie.</p>
    </div>
    """, unsafe_allow_html=True)

    st.text_input(
        "Film / Project Name",
        key="project_name"
    )
    film_length = st.selectbox("Target Film Length", ["10 seconds", "18 seconds", "1 minute", "5 minutes", "10 minutes", "50 minutes"])
    st.caption("Long films ko multiple short clips mein plan kiya jayega; ek 50-minute generation request nahi bheji jaati.")

    # Load saved scenes from Supabase
    current_project = (
        st.session_state.get("project_name") or "My First Film"
    )

    if st.session_state.get("scenes_loaded_for") != current_project:

        memories = load_ai_memories(current_project)

        saved_scenes = []

        for memory in memories:
            if memory.get("memory_type") == "scene":
                scene = dict(memory.get("content") or {})
                scene["_memory_id"] = memory.get("id")
                saved_scenes.append(scene)

        st.session_state.scenes = saved_scenes
        st.session_state.scenes_loaded_for = current_project
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Text to Video",
        "Image to Video",
        "Storyboard",
        "Audio & Dialogue",
        "Editor"
    ])

    # TEXT TO VIDEO

    with tab1:

        st.markdown("### 🎬 Create a Cinematic Scene")
        prompt_mode = st.radio("Prompt Mode", ["Manual", "Prompt Assistant"], horizontal=True)
        saved_template_rows = [row for row in load_ai_memories(current_project) if row.get("memory_type") == "other" and (row.get("content") or {}).get("kind") == "template"]
        builtin_templates = [
            {"name": "Cinematic Establishing Shot", "prompt": "Wide establishing shot of [environment], layered depth, cinematic lighting, subtle atmosphere and controlled camera movement."},
            {"name": "Anime Character Entrance", "prompt": "An expressive anime character enters the scene, detailed anime environment, readable composition, cinematic lighting and controlled motion."},
            {"name": "Emotional Close-up", "prompt": "Intimate close-up of [character] showing [emotion], subtle eye movement, shallow depth of field and soft directional lighting."},
            {"name": "Epic Action Scene", "prompt": "A clear action beat featuring [character] performing [action] in [location], dynamic tracking camera and dramatic cinematic lighting."}
        ]
        template_options = ["Start from blank"] + [item["name"] for item in builtin_templates] + [(row.get("content") or {}).get("name", row.get("title", "Custom Template")) for row in saved_template_rows]
        selected_template = st.selectbox("Start with Template", template_options)
        template_prompt = ""
        if selected_template != "Start from blank":
            all_templates = builtin_templates + [(row.get("content") or {}) for row in saved_template_rows]
            template_prompt = next((item.get("prompt", "") for item in all_templates if item.get("name") == selected_template), "")

        with st.form("scene_form"):

            scene_name = st.text_input(
                "Scene Name",
                placeholder="Example: Hero Entry"
            )

            prompt = st.text_area(
                "Describe Your Scene",
                height=150,
                value=template_prompt,
                placeholder="Describe characters, action, environment, lighting and camera movement..."
            )

            style = st.selectbox(
                "Visual Style",
                [
                    "Cinematic Realism",
                    "Anime",
                    "3D Animation",
                    "Fantasy",
                    "Sci-Fi",
                    "Horror",
                    "Documentary"
                ]
            )

            camera = st.selectbox(
                "Camera Movement",
                [
                    "Static Shot",
                    "Slow Zoom In",
                    "Slow Zoom Out",
                    "Tracking Shot",
                    "Pan Left",
                    "Pan Right",
                    "Drone Shot",
                    "Handheld"
                ]
            )

            duration = st.selectbox(
                "Scene Duration",
                ["5 seconds", "10 seconds", "15 seconds", "18 seconds", "30 seconds"]
            )

            lighting = st.selectbox("Lighting", ["Natural", "Golden Hour", "Soft Studio", "Low Key", "Neon", "Moonlight", "High Contrast", "Volumetric"])
            mood = st.selectbox("Mood", ["Hopeful", "Dramatic", "Mysterious", "Joyful", "Tense", "Melancholic", "Epic", "Peaceful"])
            aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1", "2.39:1"])
            create_scene = st.form_submit_button(
                "Build Prompt" if prompt_mode == "Prompt Assistant" else "Add Scene to Storyboard",
                use_container_width=True
            )

        if create_scene:

            if not prompt.strip():
                st.error("Scene description likho.")

            else:
                prompt = prompt.strip() + f" Visual style: {style}. Camera: {camera}. Lighting: {lighting}. Mood: {mood}. Aspect ratio: {aspect_ratio}. Maintain visual continuity."
                if prompt_mode == "Prompt Assistant":
                    st.success("Prompt structured ho gaya. Ise apne video AI tool mein use kar sakte ho.")
                    st.code(prompt)

                scene_data = {
                    "name": scene_name.strip() or f"Scene {len(st.session_state.scenes)+1}",
                    "prompt": prompt,
                    "style": style,
                    "camera": camera,
                    "duration": duration,
                    "film_length": film_length,
                    "lighting": lighting,
                    "mood": mood,
                    "aspect_ratio": aspect_ratio,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }

                success, message = save_ai_memory(
                    current_project,
                    "scene",
                    scene_data["name"],
                    scene_data
                )

                if success:
                    st.session_state.scenes_loaded_for = None
                    st.success("Scene permanently saved!")
                    st.rerun()
                else:
                    st.error(f"Save error: {message}")

        st.info(
            "Video generation engine abhi connect nahi hai. "
            "Yahan scene prompt aur production details save ki ja sakti hain."
        )

    # IMAGE TO VIDEO

    with tab2:

        st.markdown("### 🖼️ Image to Video")

        uploaded_image = st.file_uploader(
            "Upload Reference Image",
            type=["png", "jpg", "jpeg"],
            key="image_motion_upload"
        )

        motion_prompt = st.text_area(
            "Describe Image Motion",
            placeholder="Example: Character slowly turns around while camera moves closer."
        )

        motion_style = st.selectbox(
            "Motion Type",
            [
                "Slow Cinematic Motion",
                "Character Animation",
                "Camera Movement",
                "Action Motion",
                "Environment Motion"
            ]
        )

        if uploaded_image:
            st.image(
                uploaded_image,
                caption="Uploaded Reference",
                use_container_width=True
            )

        if st.button("Prepare Image Motion Prompt"):

            if uploaded_image and motion_prompt.strip():

                st.success("Reference image and motion instructions ready.")

            else:
                st.warning("Image aur motion description dono add karo.")

        st.info(
            "Image-to-video generation abhi connected nahi hai."
        )

        # STORYBOARD

    with tab3:

        st.markdown("### 📋 Your Storyboard")

        if not st.session_state.scenes:
            st.info("Abhi koi scene nahi hai. Text to Video tab se scene add karo.")

        for i, scene in enumerate(st.session_state.scenes):

            with st.expander(
                f"Scene {i+1}: {scene['name']}",
                expanded=True
            ):

                st.write("**Prompt:**", scene["prompt"])
                st.write("**Style:**", scene["style"])
                st.write("**Camera:**", scene["camera"])
                st.write("**Duration:**", scene["duration"])

                if st.button("Delete Scene", key=f"delete_scene_{i}"):

                    memory_id = scene.get("_memory_id")

                    if memory_id:
                        try:
                            get_supabase().table("ai_memory").delete().eq(
                                "id", memory_id
                            ).eq(
                                "user_id", st.session_state.user_id
                            ).execute()

                            st.session_state.scenes_loaded_for = None
                            st.success("Scene permanently deleted!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Delete error: {e}")

                    else:
                        st.session_state.scenes.pop(i)
                        st.rerun()

    
    # AUDIO
    with tab4:

        st.markdown("### 🎙️ Audio & Dialogue Studio")

        # Load saved dialogues from Supabase
        if st.session_state.get("dialogues_loaded_for") != current_project:

            memories = load_ai_memories(current_project)

            saved_dialogues = []

            for memory in memories:
                if memory.get("memory_type") == "dialogue":
                    dialogue_item = dict(memory.get("content") or {})
                    dialogue_item["_memory_id"] = memory.get("id")
                    saved_dialogues.append(dialogue_item)

            st.session_state.clips = saved_dialogues
            st.session_state.dialogues_loaded_for = current_project

        character_names = [
            c["name"] for c in st.session_state.characters
        ]

        character_options = ["No character selected"] + character_names

        with st.form("audio_form"):

            speaker = st.selectbox(
                "Character",
                character_options
            )

            dialogue = st.text_area(
                "Dialogue / Voiceover",
                placeholder="Enter your Hindi or English dialogue..."
            )

            language = st.selectbox(
                "Language",
                ["Hindi", "English", "Hinglish", "Gujarati", "Other"]
            )

            emotion = st.selectbox(
                "Emotion",
                [
                    "Normal",
                    "Happy",
                    "Sad",
                    "Angry",
                    "Excited",
                    "Whispering",
                    "Dramatic"
                ]
            )

            audio_submit = st.form_submit_button(
                "Save Dialogue"
            )

        if audio_submit:

            if not dialogue.strip():
                st.error("Dialogue likho.")

            else:

                dialogue_data = {
                    "type": "Dialogue",
                    "speaker": speaker,
                    "text": dialogue.strip(),
                    "language": language,
                    "emotion": emotion,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }

                success, message = save_ai_memory(
                    current_project,
                    "dialogue",
                    speaker,
                    dialogue_data
                )

                if success:
                    st.session_state.dialogues_loaded_for = None
                    st.success("Dialogue permanently saved!")
                    st.rerun()
                else:
                    st.error(f"Save error: {message}")

        st.markdown("### 📚 Saved Dialogues")

        if not st.session_state.clips:
            st.info("Abhi koi dialogue save nahi hua.")

        for i, clip in enumerate(st.session_state.clips):

            with st.expander(
                f"Dialogue {i+1}: {clip.get('speaker', 'Voiceover')}"
            ):

                st.write("**Dialogue:**", clip.get("text", ""))
                st.write("**Language:**", clip.get("language", ""))
                st.write("**Emotion:**", clip.get("emotion", ""))

        st.info(
            "AI voice generation aur lip-sync engine abhi connected nahi hai."
        )

    # EDITOR

    with tab5:

        st.markdown("### ✂️ Movie Editor Workspace")

        st.write("Project:", st.session_state.project_name)

        st.metric("Storyboard Scenes", len(st.session_state.scenes))
        st.metric("Dialogue Items", len(st.session_state.clips))

        st.markdown("#### Production Checklist")

        st.checkbox("Storyboard completed")
        st.checkbox("Character references checked")
        st.checkbox("Location references checked")
        st.checkbox("Voiceover prepared")
        st.checkbox("Sound effects planned")
        st.checkbox("Final video reviewed")

        st.info(
            "Timeline editing, rendering and MP4 export engine abhi connected nahi hai."
        )


# -----------------------------------------
# MY TEMPLATES
# -----------------------------------------

elif page == "🧩 My Templates":

    st.markdown("""
    <div class="hero"><h1>🧩 My Templates</h1><p>Reusable prompts for your filmmaking workflow.</p></div>
    """, unsafe_allow_html=True)
    with st.form("custom_template_form"):
        template_name = st.text_input("Template Name")
        template_category = st.selectbox("Category", ["Cinematic", "Anime", "Action", "Drama", "Fantasy", "Horror", "Commercial", "Other"])
        template_prompt = st.text_area("Prompt Template", height=150)
        save_template = st.form_submit_button("Save Template", use_container_width=True)
    if save_template:
        if not template_name.strip() or not template_prompt.strip():
            st.error("Template name aur prompt dono required hain.")
        else:
            ok, message = save_ai_memory(st.session_state.project_name, "other", template_name.strip(), {"kind": "template", "name": template_name.strip(), "category": template_category, "prompt": template_prompt.strip()})
            if ok:
                st.success("Template Supabase mein permanently save ho gaya.")
                st.rerun()
            else:
                st.error(message)
    st.markdown("### Built-in Templates")
    builtin_templates = [
        {"name": "Cinematic Establishing Shot", "category": "Cinematic", "prompt": "Wide establishing shot of [environment], layered depth, cinematic lighting, subtle atmosphere and controlled camera movement."},
        {"name": "Anime Character Entrance", "category": "Anime", "prompt": "An expressive anime character enters the scene, detailed anime environment, readable composition, cinematic lighting and controlled motion."},
        {"name": "Emotional Close-up", "category": "Drama", "prompt": "Intimate close-up of [character] showing [emotion], subtle eye movement, shallow depth of field and soft directional lighting."},
        {"name": "Epic Action Scene", "category": "Action", "prompt": "A clear action beat featuring [character] performing [action] in [location], dynamic tracking camera and dramatic lighting."}
    ]
    for item in builtin_templates:
        with st.expander(item["name"]):
            st.caption(item["category"])
            st.write(item["prompt"])
    st.markdown("### My Saved Templates")
    custom_templates = [row for row in load_ai_memories(st.session_state.project_name) if row.get("memory_type") == "other" and (row.get("content") or {}).get("kind") == "template"]
    if not custom_templates:
        st.info("Abhi koi custom template save nahi hai.")
    for row in custom_templates:
        data = row.get("content") or {}
        with st.expander(data.get("name") or row.get("title", "Template")):
            st.caption(data.get("category", "Other"))
            st.write(data.get("prompt", ""))
            if st.button("Delete Template", key=f"delete_template_{row.get('id')}"):
                try:
                    get_supabase().table("ai_memory").delete().eq("id", row.get("id")).eq("user_id", st.session_state.user_id).execute()
                    st.success("Template deleted.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Delete error: {exc}")

# -----------------------------------------
# CHARACTER LIBRARY
# -----------------------------------------

elif page == "🧑 Character Library":

    st.markdown("""
    <div class="hero">
        <h1>🧑 Character Library</h1>
        <p>Create and organize your movie characters.</p>
    </div>
    """, unsafe_allow_html=True)

    current_project = (
        st.session_state.get("project_name") or "My First Film"
    )

    # Load characters from permanent AI memory
    if st.session_state.get("characters_loaded_for") != current_project:

        memories = load_ai_memories(current_project)

        characters = []

        for memory in memories:
            if memory.get("memory_type") == "character":
                character = dict(memory.get("content") or {})
                character["_memory_id"] = memory.get("id")
                characters.append(character)

        st.session_state.characters = characters
        st.session_state.characters_loaded_for = current_project

    with st.form("character_form"):

        name = st.text_input("Character Name")

        role = st.selectbox(
            "Character Role",
            [
                "Hero",
                "Heroine",
                "Villain",
                "Supporting Character",
                "Background Character",
                "Other"
            ]
        )

        appearance = st.text_area(
            "Physical Appearance",
            placeholder="Describe face, hair, body, clothes and other visible details."
        )

        personality = st.text_area(
            "Personality",
            placeholder="Describe the character's personality."
        )

        reference = st.text_area(
            "Consistency Notes",
            placeholder="Details that must remain the same in every scene."
        )

        save_character = st.form_submit_button(
            "Save Character",
            use_container_width=True
        )

    if save_character:

        if not name.strip():
            st.error("Character name enter karo.")

        else:

            character_data = {
                "name": name.strip(),
                "role": role,
                "appearance": appearance,
                "personality": personality,
                "reference": reference
            }

            success, message = save_ai_memory(
                current_project,
                "character",
                name.strip(),
                character_data
            )

            if success:
                st.session_state.characters_loaded_for = None
                st.success("Character permanently saved!")
                st.rerun()
            else:
                st.error(f"Save error: {message}")

    st.divider()
    st.markdown("### Your Characters")

    if not st.session_state.characters:
        st.info("Abhi koi character create nahi hua.")

    for i, character in enumerate(st.session_state.characters):

        with st.expander(character.get("name", "Character")):

            st.write("**Role:**", character.get("role", ""))
            st.write("**Appearance:**", character.get("appearance", ""))
            st.write("**Personality:**", character.get("personality", ""))
            st.write("**Consistency:**", character.get("reference", ""))

            if st.button(
                "Delete Character",
                key=f"delete_character_{i}"
            ):

                memory_id = character.get("_memory_id")

                if memory_id:
                    try:
                        get_supabase().table("ai_memory").delete().eq(
                            "id", memory_id
                        ).eq(
                            "user_id", st.session_state.user_id
                        ).execute()

                        st.session_state.characters_loaded_for = None
                        st.rerun()

                    except Exception as e:
                        st.error(f"Delete error: {e}")

                else:
                    st.session_state.characters.pop(i)
                    st.rerun()


# -----------------------------------------
# LOCATION LIBRARY
# -----------------------------------------

elif page == "🌍 Location Library":

    st.markdown("""
    <div class="hero">
        <h1>🌍 Location Library</h1>
        <p>Create and permanently save your cinematic environments.</p>
    </div>
    """, unsafe_allow_html=True)

    current_project = (
        st.session_state.get("project_name") or "My First Film"
    )

    # Load locations from Supabase
    if st.session_state.get("locations_loaded_for") != current_project:

        memories = load_ai_memories(current_project)

        locations = []

        for memory in memories:
            if memory.get("memory_type") == "location":
                location = dict(memory.get("content") or {})
                location["_memory_id"] = memory.get("id")
                locations.append(location)

        st.session_state.locations = locations
        st.session_state.locations_loaded_for = current_project

    # Add new location
    with st.form("location_form"):

        location_name = st.text_input("Location Name")

        location_type = st.selectbox(
            "Environment Type",
            [
                "City", "Village", "Forest", "Mountain",
                "Desert", "Space", "Indoor",
                "Fantasy World", "Other"
            ]
        )

        description = st.text_area(
            "Environment Description",
            placeholder="Describe buildings, landscape, lighting, weather and atmosphere."
        )

        consistency = st.text_area(
            "Location Consistency Notes",
            placeholder="Details that must remain the same across scenes."
        )

        save_location = st.form_submit_button(
            "Save Location",
            use_container_width=True
        )

    if save_location:

        if not location_name.strip():
            st.error("Location name enter karo.")

        else:

            location_data = {
                "name": location_name.strip(),
                "type": location_type,
                "description": description,
                "consistency": consistency
            }

            success, message = save_ai_memory(
                current_project,
                "location",
                location_name.strip(),
                location_data
            )

            if success:
                st.session_state.locations_loaded_for = None
                st.success("Location permanently saved!")
                st.rerun()
            else:
                st.error(f"Save error: {message}")

    st.divider()
    st.markdown("### Your Saved Locations")

    if not st.session_state.locations:
        st.info("Abhi koi location create nahi hui.")

    for i, location in enumerate(st.session_state.locations):

        with st.expander(location.get("name", "Location")):

            st.write("**Type:**", location.get("type", ""))
            st.write("**Description:**", location.get("description", ""))
            st.write("**Consistency:**", location.get("consistency", ""))

            if st.button(
                "Delete Location",
                key=f"delete_location_{i}"
            ):

                memory_id = location.get("_memory_id")

                if memory_id:
                    try:
                        get_supabase().table("ai_memory").delete().eq(
                            "id", memory_id
                        ).eq(
                            "user_id", st.session_state.user_id
                        ).execute()

                        st.session_state.locations_loaded_for = None
                        st.rerun()

                    except Exception as e:
                        st.error(f"Delete error: {e}")

                else:
                    st.session_state.locations.pop(i)
                    st.rerun()


# -----------------------------------------
# ASSET LIBRARY
# -----------------------------------------

elif page == "🗂️ Asset Library":

    st.markdown("""
    <div class="hero"><h1>🗂️ Asset Library</h1><p>Private project reference images, videos, audio and files.</p></div>
    """, unsafe_allow_html=True)
    st.caption("Private Supabase bucket: studio-assets · Maximum 50 MB per file.")
    uploads = st.file_uploader("Upload project assets", type=None, accept_multiple_files=True, key="studio_asset_uploader")
    if uploads and st.button("Upload Selected Assets", use_container_width=True):
        for uploaded in uploads:
            content = uploaded.getvalue()
            if len(content) > 50 * 1024 * 1024:
                st.error(f"{uploaded.name}: 50 MB limit exceed.")
                continue
            safe_project = re.sub(r"[^A-Za-z0-9._-]+", "_", st.session_state.project_name.strip())[:70] or "project"
            safe_file = re.sub(r"[^A-Za-z0-9._-]+", "_", uploaded.name).strip("._") or "upload"
            path = f"{st.session_state.user_id}/{safe_project}/{py_secrets.token_hex(6)}_{safe_file}"
            mime = uploaded.type or "application/octet-stream"
            kind = "image" if mime.startswith("image/") else "video" if mime.startswith("video/") else "audio" if mime.startswith("audio/") else "other"
            try:
                get_supabase().storage.from_("studio-assets").upload(path, content, {"content-type": mime, "upsert": "false"})
            except Exception as exc:
                st.error(f"{uploaded.name}: upload failed: {exc}")
                continue
            try:
                get_supabase().table("studio_assets").insert({"user_id": st.session_state.user_id, "project_name": st.session_state.project_name, "bucket_id": "studio-assets", "file_path": path, "file_name": uploaded.name, "file_type": kind, "mime_type": mime, "size_bytes": len(content)}).execute()
                st.success(f"{uploaded.name}: upload complete.")
            except Exception as exc:
                try:
                    get_supabase().storage.from_("studio-assets").remove([path])
                except Exception:
                    pass
                st.error(f"{uploaded.name}: metadata save failed; rollback attempted: {exc}")
        st.rerun()
    st.markdown("### Saved Assets")
    try:
        response = get_supabase().table("studio_assets").select("*").eq("user_id", st.session_state.user_id).eq("project_name", st.session_state.project_name).order("created_at", desc=True).execute()
        assets = response.data or []
    except Exception as exc:
        assets = []
        st.error(f"Asset metadata load error: {exc}")
    search_asset = st.text_input("Search assets", placeholder="File name...")
    type_asset = st.selectbox("Filter type", ["All", "image", "video", "audio", "other"])
    assets = [item for item in assets if search_asset.lower() in (item.get("file_name") or "").lower() and (type_asset == "All" or item.get("file_type") == type_asset)]
    for asset in assets:
        with st.expander(f"{asset.get('file_name', 'Asset')} · {asset.get('file_type', 'other')}"):
            st.caption(f"{round((asset.get('size_bytes') or 0) / 1024, 1)} KB · {asset.get('created_at', '')}")
            try:
                signed_response = get_supabase().storage.from_(asset.get("bucket_id") or "studio-assets").create_signed_url(asset.get("file_path"), 3600)
                signed = None
                if isinstance(signed_response, dict):
                    signed = signed_response.get("signedURL") or signed_response.get("signedUrl") or signed_response.get("signed_url")
                if signed and asset.get("file_type") == "image":
                    st.image(signed, use_container_width=True)
                elif signed and asset.get("file_type") == "video":
                    st.video(signed)
                elif signed and asset.get("file_type") == "audio":
                    st.audio(signed)
                elif signed:
                    st.link_button("Open temporary private file link", signed)
                else:
                    st.warning("Signed preview URL create nahi hua.")
            except Exception as exc:
                st.warning(f"Preview unavailable: {exc}")
            if st.button("Delete Asset", key=f"delete_asset_{asset.get('id')}"):
                try:
                    get_supabase().storage.from_(asset.get("bucket_id") or "studio-assets").remove([asset.get("file_path")])
                    get_supabase().table("studio_assets").delete().eq("id", asset.get("id")).eq("user_id", st.session_state.user_id).execute()
                    st.success("Storage file aur metadata delete ho gaye.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Delete incomplete: {exc}")

# -----------------------------------------
# MY PROJECTS
# -----------------------------------------

elif page == "📁 My Projects":

    st.markdown("""
    <div class="hero">
        <h1>📁 My Projects</h1>
        <p>Manage and export your film projects.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Current Project")

    st.write("Project Name:", st.session_state.project_name)

    st.write("Scenes:", len(st.session_state.scenes))
    st.write("Characters:", len(st.session_state.characters))
    st.write("Locations:", len(st.session_state.locations))

    if st.button("Save Project Snapshot", use_container_width=True):

        snapshot = {
            "name": st.session_state.project_name,
            "scenes": st.session_state.scenes.copy(),
            "characters": st.session_state.characters.copy(),
            "locations": st.session_state.locations.copy(),
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        st.session_state.projects.append(snapshot)

        st.success("Project snapshot saved in this session.")
        st.rerun()

    project_data = {
        "project_name": st.session_state.project_name,
        "scenes": st.session_state.scenes,
        "characters": st.session_state.characters,
        "locations": st.session_state.locations,
        "dialogues": st.session_state.clips
    }

    st.download_button(
        "⬇️ Export Current Project JSON",
        data=json.dumps(project_data, indent=4, ensure_ascii=False),
        file_name="universe_ai_project.json",
        mime="application/json",
        use_container_width=True
    )

    st.divider()
    st.markdown("### Saved Project Snapshots")

    if not st.session_state.projects:
        st.info("Abhi koi project snapshot save nahi hua.")

    for i, project in enumerate(st.session_state.projects):

        with st.expander(project["name"]):

            st.write("Saved:", project["saved_at"])
            st.write("Scenes:", len(project["scenes"]))
            st.write("Characters:", len(project["characters"]))
            st.write("Locations:", len(project["locations"]))

            st.download_button(
                "Download Project",
                data=json.dumps(
                    project,
                    indent=4,
                    ensure_ascii=False
                ),
                file_name=f"project_{i+1}.json",
                mime="application/json",
                key=f"download_project_{i}"
            )


# -----------------------------------------
# MY PROFILE
# -----------------------------------------

elif page == "👤 My Profile":

    st.markdown("""
    <div class="hero">
        <h1>👤 My Profile</h1>
        <p>Manage your account information.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Profile Information")

    st.text_input(
        "Account Email",
        value=st.session_state.username,
        disabled=True
    )

    with st.form("profile_form"):

        new_name = st.text_input(
            "Your Display Name",
            value=st.session_state.profile_name
        )

        save_profile = st.form_submit_button(
            "Save Profile",
            use_container_width=True
        )

    if save_profile:

        try:

            get_supabase().auth.update_user({
                "data": {"full_name": new_name}
            })

            st.session_state.profile_name = new_name

            st.success("Profile name updated.")

        except Exception as e:
            st.error(f"Profile update failed: {e}")

    st.divider()
    st.markdown("### Change Email Address")

    with st.form("email_change_form"):

        new_email = st.text_input(
            "New Email Address",
            placeholder="newemail@example.com"
        ).strip().lower()

        change_email = st.form_submit_button(
            "Request Email Change"
        )

    if change_email:

        if "@" not in new_email:
            st.error("Valid email enter karo.")

        elif new_email == st.session_state.username.lower():
            st.warning("Ye email already account mein hai.")

        else:

            try:

                get_supabase().auth.update_user({
                    "email": new_email
                })

                st.success(
                    "Email change request sent. "
                    "New email par verification instructions check karo."
                )

            except Exception as e:
                st.error(f"Email update failed: {e}")

    st.divider()

    st.write("Login Method:", st.session_state.auth_method)


# -----------------------------------------
# SETTINGS
# -----------------------------------------

elif page == "⚙️ Settings":

    st.markdown("""
    <div class="hero">
        <h1>⚙️ Settings</h1>
        <p>Manage your workspace and project preferences.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Workspace Settings")

    st.text_input(
        "Default Project Name",
        key="project_name"
    )

    st.markdown("### Account")

    st.write("Email:", st.session_state.username)
    st.write("Login Method:", st.session_state.auth_method)

    st.markdown("### Workspace Information")

    st.write("Scenes:", len(st.session_state.scenes))
    st.write("Characters:", len(st.session_state.characters))
    st.write("Locations:", len(st.session_state.locations))

    st.success(
        "Supabase ai_memory database connected hai. Scenes, characters, "
        "locations aur dialogues account ke saath permanently save hote hain."
    )
    st.info(
        "Asset Library ke liye studio_assets table, private studio-assets bucket "
        "aur user-folder RLS policies configured hone chahiye."
    )
    st.info(
        "AI video generation, voice synthesis, lip-sync aur final rendering "
        "provider abhi connected nahi hai; ye workspace prompts aur production data manage karta hai."
    )

    st.markdown("### About")

    st.write("UNIVERSE AI STUDIO")
    st.write("AI Filmmaking Workspace")
    st.write("Version 1.0")


# -----------------------------------------
# FOOTER
# -----------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#888;padding:10px">
        UNIVERSE AI STUDIO · CREATE YOUR OWN UNIVERSE 🎬
    </div>
    """,
    unsafe_allow_html=True
)
