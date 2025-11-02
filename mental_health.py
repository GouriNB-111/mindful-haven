# app.py — Mindful Haven (Inspo theme, per-user data, Gemini + Games)
import os, re, time, json, random, hashlib, shutil
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# ---------- App ----------
st.set_page_config(page_title="Mindful Haven", page_icon="🧠", layout="wide")

# ---------- Theme System (Rose Bento + Sage Calm) ----------
THEMES = {
    "Rose Bento (pink)": {
        "bg_grad": "linear-gradient(180deg,#fff 0%,#fdeff4 40%,#f9dbe6 100%)",
        "panel": "#fff5f8cc",
        "card": "#f7c3d0",
        "ink": "#3b2a2e",
        "muted": "#7c6169",
        "accent": "#d36b8a",
        "accent_soft": "#fde4ec",
        "radius": "22px",
        "shadow": "0 14px 40px rgba(211,107,138,.25)",
        "headline_font": "'Playfair Display', serif",
        "body_font": "Inter, ui-sans-serif, system-ui"
    },
    "Sage Calm (green)": {
        "bg_grad": "linear-gradient(180deg,#ffffff 0%,#e9f0eb 40%,#dfe9e2 100%)",
        "panel": "#ffffffcc",
        "card": "#cfdccf",
        "ink": "#273026",
        "muted": "#5f6b60",
        "accent": "#7aa184",
        "accent_soft": "#e9f3ec",
        "radius": "22px",
        "shadow": "0 14px 40px rgba(122,161,132,.25)",
        "headline_font": "'Playfair Display', serif",
        "body_font": "Inter, ui-sans-serif, system-ui"
    }
}

def inject_theme(theme):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@500;700&display=swap');
    :root{{
      --bg-grad: {theme['bg_grad']};
      --panel: {theme['panel']};
      --card: {theme['card']};
      --ink: {theme['ink']};
      --muted: {theme['muted']};
      --accent: {theme['accent']};
      --accent-soft: {theme['accent_soft']};
      --radius: {theme['radius']};
      --shadow: {theme['shadow']};
      --hfont: {theme['headline_font']};
      --bfont: {theme['body_font']};
    }}
    html, body {{ background: var(--bg-grad); }}
    * {{ font-family: var(--bfont); color: var(--ink); }}
    h1,h2,h3,h4 {{ font-family: var(--hfont); letter-spacing:.2px; color: var(--ink); }}
    .hero {{
      background: radial-gradient(1200px 600px at -10% -10%, var(--accent-soft) 0%, #0000 60%),
                  radial-gradient(900px 500px at 110% -20%, #fff 0%, #0000 60%);
      border-radius: 28px; padding: 28px; box-shadow: var(--shadow);
      border: 1px solid rgba(0,0,0,.05);
    }}
    .pin-card{{ background:var(--panel); border-radius:var(--radius); box-shadow:var(--shadow); border:1px solid rgba(0,0,0,.06); padding:16px; margin-bottom:16px; backdrop-filter:blur(8px); }}
    .pin-grid{{ column-count:1; column-gap:16px; }}
    @media(min-width:760px){{ .pin-grid{{ column-count:2; }} }}
    @media(min-width:1180px){{ .pin-grid{{ column-count:3; }} }}
    .chat-msg{{ padding:12px 14px; border-radius:16px; margin:8px 0; max-width:95%; }}
    .chat-user{{ background:#fff; border:1px solid rgba(0,0,0,.08); }}
    .chat-assistant{{ background:var(--accent-soft); }}
    .muted{{ color:var(--muted); }}
    .kpi{{ background: var(--panel); border-radius: 16px; padding:14px 16px; box-shadow: var(--shadow); }}
    .kpi .lbl{{ font-size:.85rem; color:var(--muted); }}
    .kpi .val{{ font-size:1.4rem; font-weight:700; }}
    .sidebar-card{{ background:var(--panel); border-radius:16px; padding:14px; box-shadow:var(--shadow); border:1px solid rgba(0,0,0,.05); }}
    .chip{{ display:inline-block; padding:6px 10px; border-radius:999px; background: var(--accent-soft); margin-right:6px; }}
    </style>
    """, unsafe_allow_html=True)

# Use a fixed default theme (can change to "Sage Calm (green)" if you prefer)
_theme = "Rose Bento (pink)"
inject_theme(THEMES[_theme])

# --------- Safety / Disclaimer panel ---------
# --------- Minimal, Pinterest-style disclaimer ---------
st.sidebar.markdown("""
<div class="sidebar-card" style="
  background:var(--panel);
  border-left:4px solid var(--accent);
  padding:10px 14px;
  border-radius:16px;
  box-shadow:var(--shadow);
">
  <div style="font-weight:600; color:var(--ink);">
    ⚠️ Gentle Reminder
  </div>
  <div style="font-size:0.9rem; color:var(--muted); line-height:1.35; margin-top:4px;">
    Mindful Haven offers support & calm tools — 
    not a substitute for professional help 🌸
  </div>
</div>
""", unsafe_allow_html=True)


# >>> place immediately after inject_theme(THEMES[_theme])
st.markdown("""
<style>
/* ---------- Pinterest-y buttons (global) ---------- */
.stButton > button{
  width: 100%;
  padding: 14px 18px;
  border-radius: 18px;
  border: 1px solid rgba(0,0,0,.06);
  background: linear-gradient(180deg,#ffffff, #fff7fb);
  color: var(--ink);
  font-weight: 700;
  letter-spacing: .2px;
  box-shadow:
    0 14px 30px rgba(211,107,138,.12),
    0 2px 0 rgba(255,255,255,.85) inset;
  transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
}

/* Hover / active lift */
.stButton > button:hover{
  transform: translateY(-2px);
  box-shadow:
    0 18px 40px rgba(211,107,138,.18),
    0 2px 0 rgba(255,255,255,.95) inset;
  filter: saturate(1.02);
}
.stButton > button:active{
  transform: translateY(0);
  box-shadow:
    0 8px 18px rgba(211,107,138,.14),
    0 1px 0 rgba(255,255,255,.9) inset;
}

/* Subtle focus ring (accessible) */
.stButton > button:focus{
  outline: 2px solid rgba(211,107,138,.55) !important;
  outline-offset: 2px;
}

/* Make your two hero CTAs feel bigger (first row of buttons after H1) */
.block-container .stButton:first-child button,
.block-container .stButton:nth-child(2) button{
  padding: 16px 20px;
  border-radius: 20px;
  font-size: 1.05rem;
}

/* Optional: tiny, rounded "chip" nav vibe matches Pinterest */
.stButton > button:not(:hover){
  background-clip: padding-box;
}

/* ---------- (Optional) Neutralizer for places you DON'T want this look ----------
Wrap a section with:
st.markdown('<div class="btn-neutral">', unsafe_allow_html=True)
...your widgets...
st.markdown('</div>', unsafe_allow_html=True)
*/
.btn-neutral .stButton > button{
  border-radius: 8px;
  background: #fff;
  box-shadow: none;
  font-weight: 600;
}
.btn-neutral .stButton > button:hover{
  transform:none; box-shadow:none; filter:none;
}
</style>
""", unsafe_allow_html=True)


# ---------- Small nav helper ----------
def _nav_to(name: str, **state):
    for k, v in state.items():
        st.session_state[k] = v
    st.session_state["_nav"] = name
    st.rerun()

# ---------- API ----------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found. Put GOOGLE_API_KEY=... in .env")
    st.stop()
genai.configure(api_key=API_KEY)
RAW_MODEL = os.getenv("GENAI_MODEL", "gemini-2.5-flash-lite").strip()
def normalize_model(name: str) -> str:
    banned = ("preview","exp")
    if any(b in name.lower() for b in banned): return "models/gemini-2.5-flash-lite"
    return name if name.startswith("models/") else f"models/{name}"
MODEL = normalize_model(RAW_MODEL)

# --- Do NOT ping Gemini globally (prevents 429s on every rerun) ---
def require_gemini():
    return True  # keep for compatibility; callers can still use try/except locally

# ---------- Per-user storage (username + optional PIN) ----------
st.sidebar.markdown("### 👤 Profile")
username = st.sidebar.text_input("Your name or ID", value="", placeholder="Enter your name")
pin = st.sidebar.text_input("4-digit PIN (optional)", value="", type="password", placeholder="1234")

# ---------- Assets ----------
ASSETS_DIR = Path("assets")
def pick_asset(basename: str):
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = ASSETS_DIR / f"{basename}.{ext}"
        if p.exists():
            return p
    return ASSETS_DIR / f"{basename}.jpeg"

LOGO_PRIMARY = pick_asset("logo_primary")      # your app logo (image 2)
POSTER_OKAY  = pick_asset("poster_okay")       # “It’s okay to not be okay” (image 1)
NUTRITION_BANNER = pick_asset("nutrition_banner")
NUTRITION_SIDE   = pick_asset("nutrition_side")

# ---------- Not logged-in (only poster) ----------
if not username.strip():
    st.markdown(
        """
        <div class="hero" style="text-align:center;">
          <h2 style="margin-top:0;">Welcome to Mindful Haven</h2>
          <div class="muted">Enter your name (and optional PIN) in the left sidebar to unlock your private space.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if POSTER_OKAY.exists():
        st.image(str(POSTER_OKAY), use_column_width=True)
    else:
        st.info("Add assets/poster_okay.(png/jpg/jpeg/webp)")
    st.stop()

# ---------- User folder ----------
def uid(name: str, pin: str="") -> str:
    return hashlib.sha1((name.strip().lower()+"|"+(pin or "")).encode()).hexdigest()[:10]

USER_ID = uid(username, pin)
USER_DIR = Path("data") / USER_ID
USER_DIR.mkdir(parents=True, exist_ok=True)
st.sidebar.caption(f"Profile ID: `{USER_ID}`")

# Show logo under Profile ID (per your request)
if LOGO_PRIMARY.exists():
    st.sidebar.image(str(LOGO_PRIMARY), use_column_width=True)

# ---------- Paths ----------
JOURNAL_CSV = USER_DIR / "journal.csv"
CHECKINS_JSON = USER_DIR / "checkins.json"
HABITS_CSV = USER_DIR / "habits.csv"
GRATITUDE_JSON = USER_DIR / "gratitude.json"
NOTES_TXT = USER_DIR / "session_notes.txt"
GAMES_JSON = USER_DIR / "games.json"
# --- Nutrition files ---
NUTRITION_JSON = USER_DIR / "nutrition_day.json"        # per-day entries (dict keyed by date)
NUTRITION_GOALS_JSON = USER_DIR / "nutrition_goals.json"  # weekly goals + checklist
MOODY_JSON = USER_DIR / "moody_melody.json"
AUDIO_DIR = USER_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)



# ---------- State ----------
ss = st.session_state
def df_safe(path: Path, cols):
    if path.exists():
        try: return pd.read_csv(path)
        except Exception: pass
    return pd.DataFrame(columns=cols)

def load_json(path: Path, default):
    try:
        if path.exists() and path.stat().st_size > 0:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

ss.setdefault("chat", [])
ss.setdefault("journal_df", df_safe(JOURNAL_CSV, ["date","mood_1to5","emotion","note"]))
ss.setdefault("gratitude", load_json(GRATITUDE_JSON, []))
ss.setdefault("habits", df_safe(HABITS_CSV, ["Date","Habit","Done"]))
ss.setdefault("reflection_answers", [""]*5)
ss.setdefault("last_was_stress", False)
ss.setdefault("exercise_streak", 0)
ss.setdefault("reflection_streak", 0)
ss.setdefault("last_tone", "neutral")
ss.setdefault("games", load_json(GAMES_JSON, {"reaction": [], "stroop_best": 0}))
ss.setdefault("current_page", "🏠 Home")
# --- Nutrition state defaults ---
today_str = time.strftime("%Y-%m-%d")
ss.setdefault("nutrition_day", load_json(NUTRITION_JSON, {}))     # {date: {...}}
ss.setdefault("nutrition_goals", load_json(NUTRITION_GOALS_JSON, {
    "goals": ["Drink 3L water", "Eat 5 servings veggies", "No sugary drink 5/7 days"],
    "weekly_checks": {d: {"Fruit": False, "Veggies": False, "No sugary drink": False} for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]}
}))
if today_str not in ss.nutrition_day:
    ss.nutrition_day[today_str] = {
        "water_glasses": 0,            # 0..12
        "breakfast": "", "lunch": "", "dinner": "", "snacks": "",
        "calories": 0, "protein": 0, "carbs": 0, "fat": 0,
        "notes": "", "mood_after_meals": 3  # 1..5
    }
ss.setdefault("melody", load_json(MOODY_JSON, {
    "playlists": {
        "Calm Mix": []  # list of tracks dicts
    },
    "current": "Calm Mix"
}))



# ---------- Persistence helpers ----------
def save_journal(df):
    df.to_csv(JOURNAL_CSV, index=False)
    ss.journal_df = df

def save_checkin(answers):
    data = []
    if CHECKINS_JSON.exists() and CHECKINS_JSON.stat().st_size>0:
        try: data = json.load(open(CHECKINS_JSON))
        except Exception: data = []
    data.append({"answers":answers, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
    json.dump(data, open(CHECKINS_JSON,"w"), indent=2)

def save_gratitude():
    json.dump(ss.gratitude, open(GRATITUDE_JSON,"w"), indent=2)

def save_habits():
    ss.habits.to_csv(HABITS_CSV, index=False)

def save_games():
    json.dump(ss.games, open(GAMES_JSON,"w"), indent=2)

def save_nutrition_day():
    json.dump(ss.nutrition_day, open(NUTRITION_JSON, "w"), indent=2)

def save_nutrition_goals():
    json.dump(ss.nutrition_goals, open(NUTRITION_GOALS_JSON, "w"), indent=2)

def save_melody():
    json.dump(ss.melody, open(MOODY_JSON, "w"), indent=2)



# ---------- Safety & Emotion ----------
CRISIS = [r"\bi want to die\b", r"\bsuicide\b", r"\bkill myself\b", r"\bself[- ]harm\b", r"\bending it all\b", r"\bno reason to live\b"]
def crisis(text): t=text.lower().strip(); return any(re.search(p,t) for p in CRISIS)
def stress(text): t=text.lower(); return any(w in t for w in ["stress","anxiety","overwhelmed","panic","sad","lonely","depressed","tired"])
def tone(text):
    t=text.lower()
    pos=any(x in t for x in ["grateful","hopeful","better","calm","good","proud","glad","relieved"])
    neg=any(x in t for x in ["anxious","panic","sad","angry","overwhelmed","tired","drained","depressed","worthless"])
    if pos and not neg: return "positive"
    if neg and not pos: return "negative"
    return "neutral"

HELPLINES = [
    "KIRAN (India): 1800 599 0019",
    "Tele-MANAS (India): 080-4611 0007 / 14416",
    "iCALL (India): 9152987821",
]
AFFIRM = [
    "You are stronger than you think.",
    "Every step you take is progress.",
    "It’s okay to take up space and rest.",
    "This wave will pass.",
    "Be gentle with yourself today.",
]

# ---------- Hero Header (top center nav only) ----------
with st.container():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.4, 1])
    with col1:
        st.markdown("<h1 style='margin:0;'>Mindful Haven</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='muted' style='margin-top:6px;'>Hi <b>{username}</b> — a gentle space for journaling, reflection & support.</div>", unsafe_allow_html=True)
        cta1, cta2 = st.columns([0.35, 0.45])
        with cta1:
            if st.button("Start chatting", key="hero_chat", use_container_width=True):
                _nav_to("💬 Chat")
        with cta2:
            if st.button("Write a reflection", key="hero_journal", use_container_width=True):
                _nav_to("📓 Journal")
    with col2:
        st.markdown("<div style='text-align:right; margin-top:8px;'>"
                    "<span class='chip'>calm</span> "
                    "<span class='chip'>supportive</span> "
                    "<span class='chip'>private</span></div>", unsafe_allow_html=True)

    # --- Top nav (Nutrition between Journal and Tools) ---
    nav_home, nav_chat, nav_journal, nav_nutri, nav_tools, nav_games, nav_habits, nav_progress = st.columns(8)

    if nav_home.button("🏠Home"): _nav_to("🏠 Home")
    if nav_chat.button("💬Chat"): _nav_to("💬 Chat")
    if nav_journal.button("📓Journal"): _nav_to("📓 Journal")
    if nav_nutri.button("🍎Nutrition"): _nav_to("🍎 Nutrition")
    if nav_tools.button("🧩 Tools"): _nav_to("🧩 Tools")
    if nav_games.button("🎮 Games"): _nav_to("🎮 Games")
    if nav_habits.button("🎵Music"): _nav_to("🎵 Music") 
    if nav_progress.button("📈Progress"): _nav_to("📈 Progress")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Prompt of the day + Quick Calm bar (global, below hero) ---
with st.expander("📝 Prompt of the day", expanded=False):
    prompts = [
        "What felt lighter today than yesterday?",
        "A small moment of kindness you noticed:",
        "If stress could talk, what would it ask for?",
        "One thing future-you will thank you for:",
        "A place that feels safe and why:",
    ]
    idx = int(time.strftime("%j")) % len(prompts)
    st.markdown(f"> {prompts[idx]}")
    if st.button("Use in Journal"):
        ss["_nav"] = "📓 Journal"
        # prefill Q1 with the prompt
        ss.reflection_answers[0] = prompts[idx]
        st.rerun()


# central navigation state (no sidebar radio)
page = ss.pop("_nav", ss.get("current_page", "🏠 Home"))
ss.current_page = page

# ---------- Pages ----------
if page == "🏠 Home":
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f"<div class='kpi'><div class='lbl'>Reflections</div><div class='val'>{len(ss.journal_df)}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi'><div class='lbl'>Gratitudes</div><div class='val'>{len(ss.gratitude)}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi'><div class='lbl'>Habits</div><div class='val'>{len(ss.habits)}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='kpi'><div class='lbl'>Breath Sessions</div><div class='val'>{ss.exercise_streak}</div></div>", unsafe_allow_html=True)

    st.write("")
    colA, colB = st.columns([1.4,1])
    with colA:
        st.subheader("Today’s Quick Check-in")
        m = st.slider("Mood (1–5)", 1, 5, 3, key="home_mood")
        note = st.text_input("One-line note")
        if st.button("Save quick check-in"):
            row = {"date": time.strftime("%Y-%m-%d"), "mood_1to5": m, "emotion": tone(note), "note": note}
            df = ss.journal_df
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            save_journal(df)
            ss.reflection_streak += 1
            if m <= 2:
                with st.expander("Helplines (India)"):
                    for h in HELPLINES: st.markdown(f"- {h}")
            st.success("Saved ✓")

        st.subheader("Gratitude Wall")
        g = st.text_input("I’m grateful for...")
        if st.button("Add gratitude"):
            if g.strip():
                ss.gratitude.append(f"{time.strftime('%Y-%m-%d')}: {g.strip()}")
                save_gratitude()
        if ss.gratitude:
            st.markdown("<div class='pin-grid'>" + "".join(
                [f"<div class='pin-card'><b>{x.split(':',1)[0]}</b><br>{x.split(':',1)[1].strip()}</div>"
                 for x in ss.gratitude[-12:]]
            ) + "</div>", unsafe_allow_html=True)

    with colB:
        st.subheader("Mini Grounding")
        if st.button("5-4-3-2-1 Exercise", use_container_width=True):
            st.info("Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.")
        if st.button("One kind thing for yourself", use_container_width=True):
            st.success(random.choice(AFFIRM))
        st.subheader("Session Notes")
        notes = st.text_area("Jot down anything to remember later", value=NOTES_TXT.read_text() if NOTES_TXT.exists() else "", height=180)
        if st.button("Save notes", use_container_width=True):
            NOTES_TXT.write_text(notes)
            st.success("Notes saved.")

    st.write("")
    # Home poster (image 1)
    if POSTER_OKAY.exists():
        st.image(str(POSTER_OKAY), use_column_width=True)

elif page == "💬 Chat":
    left, right = st.columns([1.5,1], gap="large")
    with left:
        st.subheader("I’m here to listen")
        u = st.chat_input("How are you feeling today?")
        if u:
            ss.last_tone = tone(u)
            if crisis(u):
                ss.chat.append(("assistant",
                    "I’m really glad you told me. If you’re in immediate danger or considering self-harm, "
                    "please reach out to local emergency services or someone you trust right now. You deserve support."))
                with st.expander("Helplines (India)"):
                    for h in HELPLINES: st.markdown(f"- {h}")
            else:
                ss.chat.append(("user", u))
                ss.last_was_stress = stress(u)
                try:
                    m = genai.GenerativeModel(MODEL)
                    r = m.generate_content(
                        "You are a warm AI therapist. Validate feelings, avoid diagnosis. "
                        "Offer one gentle suggestion or grounding step if appropriate.\n\nUser: "+u,
                        generation_config={"temperature":0.7,"max_output_tokens":350}
                    )
                    reply = (getattr(r,"text","") or "").strip() or \
                            "I’m here with you. What would feel supportive in this moment?"
                except Exception:
                    reply = "Let’s try a quick grounding: 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste."
                ss.chat.append(("assistant", reply))

        for role,msg in ss.chat[-60:]:
            cls = "chat-user" if role=="user" else "chat-assistant"
            st.markdown(f"<div class='chat-msg {cls}'>{msg}</div>", unsafe_allow_html=True)

        if ss.last_was_stress:
            st.write("")
            st.subheader("Suggestions")
            c1,c2,c3 = st.columns(3)
            if c1.button("🌬 4-7-8", use_container_width=True): _nav_to("🧩 Tools", tool_tab="breathing")
            if c2.button("🧠 CBT Reframe", use_container_width=True): _nav_to("🧩 Tools", tool_tab="cbt")
            if c3.button("💖 Affirmation", use_container_width=True): st.success(random.choice(AFFIRM))

    with right:
        st.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
        st.subheader("Quick Emotion Sense")
        st.info(ss.get("last_tone", "neutral"))
        st.subheader("SOS")
        with st.expander("Helplines (India)"):
            for h in HELPLINES: st.markdown(f"- {h}")
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "📓 Journal":
    from datetime import datetime, timedelta

    st.subheader("Daily Reflection")

    # ---------- Ensure DataFrame structure ----------
    df = ss.journal_df.copy()
    for col in ["date", "mood_1to5", "emotion", "note"]:
        if col not in df.columns:
            df[col] = "" if col != "mood_1to5" else None
    ss.journal_df = df

    # ---------- Reflection form ----------
    qs = [
        "1) Highlight of your day",
        "2) What challenged you",
        "3) Stress/anxiety & how you coped",
        "4) Something you’re grateful for",
    ]
    c1, c2 = st.columns([1.2, 1])
    with c1:
        if not isinstance(ss.reflection_answers, list) or len(ss.reflection_answers) < 5:
            ss.reflection_answers = (ss.reflection_answers + [""] * 5)[:5]

        ans = []
        for i, q in enumerate(qs):
            val = st.text_input(q, value=ss.reflection_answers[i], key=f"ref_{i}")
            ans.append(val)

        # Mood as slider (no crash on invalid input)
        mood = st.slider("5) Mood 1–5", 1, 5, 3, key="ref_mood_slider")

        if st.button("Save reflection"):
            ss.reflection_answers[:4] = ans[:4]
            row = {
                "date": time.strftime("%Y-%m-%d"),
                "mood_1to5": int(mood),
                "emotion": tone(" ".join(ans[:4])),
                "note": ans[0] or "",
            }
            df = ss.journal_df.copy()
            df["mood_1to5"] = pd.to_numeric(df["mood_1to5"], errors="coerce")
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            save_journal(df)

            if int(mood) <= 2:
                with st.expander("Helplines (India)"):
                    for h in HELPLINES:
                        st.markdown(f"- {h}")
            st.success("Saved ✓")

    with c2:
        st.markdown(
            "<div class='pin-card'><b>Tips</b><br>"
            "<span class='small'>Write a few honest sentences. You can track mood trends later.</span></div>",
            unsafe_allow_html=True,
        )

    # ---------- Search & view reflections ----------
    st.write("")
    df = ss.journal_df.copy()
    if df.empty:
        st.info("No entries yet — add your first reflection.")
    else:
        q = st.text_input("Search reflections", placeholder="Search by note or emotion...")
        df["note"] = df["note"].fillna("")
        df["emotion"] = df["emotion"].fillna("")

        if q:
            ql = q.lower().strip()
            df = df[df.apply(
                lambda r: ql in r["note"].lower() or ql in r["emotion"].lower(),
                axis=1
            )]

        if df.empty:
            st.info("No matching entries.")
        else:
            cards = []
            for _, r in df.tail(12).iterrows():
                cards.append(
                    f"<div class='pin-card'><h4 style='margin:.2rem 0'>{r.get('date','')}</h4>"
                    f"<div class='small muted'>Mood: {r.get('mood_1to5','')}/5 • Emotion: <b>{r.get('emotion','')}</b></div>"
                    f"<p>{(r.get('note','') or '')[:220]}</p></div>"
                )
            st.markdown("<div class='pin-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)

    # ---------- Reflection streaks ----------
    df_streak = ss.journal_df.copy()
    if not df_streak.empty and "date" in df_streak.columns:
        dts = pd.to_datetime(df_streak["date"], errors="coerce").dropna().dt.date
        if not dts.empty:
            today = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
            present = set(sorted(dts.unique()))
            streak, cursor = 0, today
            while cursor in present:
                streak += 1
                cursor = cursor - timedelta(days=1)
            badge = "🌱" if streak >= 1 else ""
            if streak >= 3: badge = "🌿"
            if streak >= 7: badge = "🌸"
            if streak >= 14: badge = "🌷"
            if streak >= 30: badge = "💮"
            st.markdown(
                f"<div class='pin-card'>Reflection streak: <b>{int(streak)}</b> days {badge}</div>",
                unsafe_allow_html=True,
            )

elif page == "🍎 Nutrition":
    st.subheader("Weekly Nutrition Planner")
    st.caption("Small steps every day 🌷")

    # --- Top banner ---
    if NUTRITION_BANNER.exists():
        st.image(str(NUTRITION_BANNER), use_column_width=True)
    else:
        st.markdown(
            "<div class='pin-card' style='height:150px;"
            "background:linear-gradient(180deg,#ffe8f1,#f9dbe6);"
            "border-radius:22px'></div>", unsafe_allow_html=True
        )

    # --- Goals header card ---
    st.markdown(
        "<div class='pin-card' style='display:flex;align-items:center;gap:14px;margin-top:8px'>"
        "<div style='width:56px;height:40px;border-radius:10px;"
        "background:linear-gradient(135deg,#ffdfe9,#f9cbdc);border:1px solid rgba(0,0,0,.05)'></div>"
        "<div><b>Goals</b><div class='muted' style='font-size:.85rem'>this week</div></div>"
        "</div>", unsafe_allow_html=True
    )

    # ---------- normalize weekly_checks so keys always exist ----------
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    habits = ["Fruit", "Veggies", "No sugary drink"]
    checks = ss.nutrition_goals.get("weekly_checks", {})
    changed_init = False
    for d in days:
        row = checks.get(d, {})
        for h in habits:
            if h not in row:
                row[h] = False
                changed_init = True
        checks[d] = row
    if changed_init:
        ss.nutrition_goals["weekly_checks"] = checks
        save_nutrition_goals()

    # --- Goals editor (left) + Side image (right, keep placement same) ---
    gcol, scol = st.columns([1.2, 1])
    with gcol:
        goals_list = ss.nutrition_goals.get("goals", [])
        for i, gtxt in enumerate(list(goals_list)):
            r1, r2 = st.columns([0.9, 0.1])
            with r1:
                goals_list[i] = st.text_input(f"Goal {i+1}", value=gtxt, key=f"ng_goal_{i}")
            with r2:
                if st.button("✖", key=f"ng_del_{i}"):
                    goals_list.pop(i)
                    ss.nutrition_goals["goals"] = goals_list
                    save_nutrition_goals()
                    st.rerun()

        newg = st.text_input("➕ Add a new weekly goal", key="ng_add_goal")
        if newg.strip() and st.button("Add goal", key="ng_add_btn"):
            goals_list.append(newg.strip())
            ss.nutrition_goals["goals"] = goals_list
            save_nutrition_goals()
            st.rerun()

        ss.nutrition_goals["goals"] = goals_list
        save_nutrition_goals()

    with scol:
        # 🖼️ Keep NUTRITION_SIDE here (same placement)
        if NUTRITION_SIDE.exists():
            st.image(str(NUTRITION_SIDE), use_column_width=True)

    st.markdown("---")

    # --- Two main columns (Today + Checklist/Progress) ---
    left, right = st.columns([1.4, 1])

    # ===== LEFT: Today card =====
    with left:
        st.markdown("### Today")
        day = ss.nutrition_day[today_str]

        st.markdown("**Hydration**")
        st.caption("Tap to add a glass (250ml)")
        gl_cols = st.columns(12)
        for i in range(12):
            filled = i < day["water_glasses"]
            label = "💧" if filled else "○"
            if gl_cols[i].button(label, key=f"water_{i}"):
                day["water_glasses"] = min(12, day["water_glasses"] + 1)
                ss.nutrition_day[today_str] = day
                save_nutrition_day()
                st.rerun()

        c1, c2 = st.columns(2)
        if c1.button("Reset water"):
            day["water_glasses"] = 0
            ss.nutrition_day[today_str] = day
            save_nutrition_day()
            st.rerun()
        c2.caption(f"Total: **{day['water_glasses']}** glasses")

        st.markdown("**Meals**")
        day["breakfast"] = st.text_area("🍳 Breakfast", value=day["breakfast"], height=70)
        day["lunch"]     = st.text_area("🥗 Lunch", value=day["lunch"], height=70)
        day["dinner"]    = st.text_area("🍲 Dinner", value=day["dinner"], height=70)
        day["snacks"]    = st.text_area("🍪 Snacks", value=day["snacks"], height=60)

        st.markdown("**Macros (approx.)**")
        m1, m2, m3, m4 = st.columns(4)
        day["calories"] = m1.number_input("kcal", 0, 10000, value=int(day["calories"]))
        day["protein"]  = m2.number_input("Protein (g)", 0, 500, value=int(day["protein"]))
        day["carbs"]    = m3.number_input("Carbs (g)", 0, 800, value=int(day["carbs"]))
        day["fat"]      = m4.number_input("Fat (g)", 0, 300, value=int(day["fat"]))

        n1, n2 = st.columns([1, 1])
        with n1:
            day["mood_after_meals"] = st.slider("How did your body feel?", 1, 5, int(day["mood_after_meals"]))
        with n2:
            day["notes"] = st.text_input("Note (optional)", value=day["notes"])

        if st.button("Save today"):
            ss.nutrition_day[today_str] = day
            save_nutrition_day()
            st.success("Saved ✓")

    # ===== RIGHT: Checklist (first), then Progress =====
    with right:
        st.markdown("### Weekly Checklist")
        checks = ss.nutrition_goals.get("weekly_checks", {})
        for d in days:
            row = checks.get(d, {h: False for h in habits})
            cols = st.columns(4)
            cols[0].markdown(f"**{d}**")
            for j, h in enumerate(habits):
                row[h] = cols[j + 1].checkbox(h, value=bool(row.get(h, False)), key=f"chk_{d}_{h}")
            checks[d] = row

        ss.nutrition_goals["weekly_checks"] = checks
        save_nutrition_goals()

        st.markdown("### Weekly Progress")
        def pct(habit: str) -> float:
            true_count = sum(1 for d in days if checks.get(d, {}).get(habit, False))
            return round(true_count / len(days) * 100, 1)

        for h in habits:
            pc = pct(h)
            st.markdown(f"{h} — **{pc}%** (_{sum(1 for d in days if checks.get(d, {}).get(h, False))}/7 days_)")
            st.progress(pc / 100)

        st.markdown("### This Week at a Glance")

        # Build last 7 actual dates as datetimes
        end = pd.Timestamp.today().normalize()
        dates = pd.date_range(end - pd.Timedelta(days=6), end, freq="D")

        rows = []
        for dt in dates:
          key = dt.strftime("%Y-%m-%d")
          ent = ss.nutrition_day.get(key, {})
          rows.append({
              "date": dt,                                   # datetime for proper axis
              "kcal": int(ent.get("calories", 0)),
              "water": int(ent.get("water_glasses", 0)),
          })

        dfwk = pd.DataFrame(rows)

        if not dfwk.empty:
           if dfwk["kcal"].sum() > 0:
            # Calories line (only if you actually logged some)
              fig = px.line(
              dfwk, x="date", y="kcal", markers=True, title="Calories (last 7 days)",
              color_discrete_sequence=["#d36b8a"]
              )
           else:
            # Fallback: Hydration bar (more useful than a flat zero line)
               fig = px.bar(
               dfwk, x="date", y="water", title="Hydration — glasses (last 7 days)",
               color_discrete_sequence=["#f7b8d4"]
              )

           fig.update_layout(
              margin=dict(l=10, r=10, t=40, b=0),
              height=260,
              xaxis=dict(tickformat="%b %d")  # e.g., Nov 02
            )
           st.plotly_chart(fig, use_container_width=True)
        else:
           st.info("No data for the last 7 days yet.")


    st.markdown("---")

    # --- Export ---
    st.subheader("Export Data")
    rows = []
    for d, ent in ss.nutrition_day.items():
        rows.append({
            "date": d,
            "water_glasses": ent.get("water_glasses", 0),
            "calories": ent.get("calories", 0),
            "protein": ent.get("protein", 0),
            "carbs": ent.get("carbs", 0),
            "fat": ent.get("fat", 0),
            "mood_after_meals": ent.get("mood_after_meals", 3),
            "breakfast": ent.get("breakfast", ""),
            "lunch": ent.get("lunch", ""),
            "dinner": ent.get("dinner", ""),
            "snacks": ent.get("snacks", ""),
            "notes": ent.get("notes", ""),
        })
    df_nut = pd.DataFrame(rows).sort_values("date")
    st.download_button("⬇️ Download nutrition.csv", data=df_nut.to_csv(index=False).encode(),
                       file_name=f"nutrition_{USER_ID}.csv")


elif page == "🧩 Tools":
    st.subheader("Wellness Tools")

    # -------------------- ✅ Habits (simple) --------------------
    st.markdown("### Habits (daily)")

    colA, colB = st.columns([1.5, .5])
    with colA:
        new_habit = st.text_input("New habit", placeholder="Sleep by 11pm")
    with colB:
        add_clicked = st.button("Add habit", use_container_width=True)

    if add_clicked and (new_habit or "").strip():
        ss.habits = pd.concat(
            [ss.habits, pd.DataFrame([{"Date": today_str, "Habit": new_habit.strip(), "Done": 0}])],
            ignore_index=True
        )
        save_habits()
        st.success("Added ✓")
        st.rerun()

    if ss.habits.empty:
        st.caption("No habits yet — add one above.")
    else:
        names = sorted(set(ss.habits["Habit"].astype(str).tolist()))
        done_today = 0

        for i, h in enumerate(names):
            mask_today = (ss.habits["Date"] == today_str) & (ss.habits["Habit"] == h)
            is_done = bool(int(ss.habits.loc[mask_today, "Done"].max())) if mask_today.any() else False

            c1, c2, c3 = st.columns([0.09, 0.71, 0.20])
            tick = c1.checkbox("", value=is_done, key=f"tool_h_{i}")
            c2.write(h)
            del_clicked = c3.button("Delete", key=f"tool_del_{i}")

            # Toggle save
            if tick != is_done:
                if mask_today.any():
                    ss.habits.loc[mask_today, "Done"] = int(tick)
                else:
                    ss.habits = pd.concat(
                        [ss.habits, pd.DataFrame([{"Date": today_str, "Habit": h, "Done": int(tick)}])],
                        ignore_index=True
                    )
                save_habits()
            if tick:
                done_today += 1

            # Delete all rows of that habit name
            if del_clicked:
                ss.habits = ss.habits[ss.habits["Habit"] != h].reset_index(drop=True)
                save_habits()
                st.rerun()

        # Progress for today
        st.progress(done_today / max(1, len(names)))
        st.caption(f"Today: {done_today}/{len(names)} habits")

        a1, a2 = st.columns(2)
        if a1.button("Mark all done for today"):
            for h in names:
                mask = (ss.habits["Date"] == today_str) & (ss.habits["Habit"] == h)
                if mask.any():
                    ss.habits.loc[mask, "Done"] = 1
                else:
                    ss.habits = pd.concat(
                        [ss.habits, pd.DataFrame([{"Date": today_str, "Habit": h, "Done": 1}])],
                        ignore_index=True
                    )
            save_habits()
            st.rerun()

        if a2.button("Clear today's ticks"):
            ss.habits.loc[ss.habits["Date"] == today_str, "Done"] = 0
            save_habits()
            st.rerun()

    st.write("---")

    # -------------------- Your tool tabs (unchanged) --------------------
    default_tab = ss.get("tool_tab", "breathing")
    t1, t2, t3 = st.tabs(["🫁 Breathing", "🧠 CBT Reframe", "🌿 Grounding"])
    ss["tool_tab"] = default_tab

    with t1:
        st.caption("4–7–8 for anxiety · Box breathing for focus")
        mode = st.radio("Mode", ["4-7-8", "Box (4-4-4-4)"], horizontal=True, index=0)
        cycles = st.slider("Cycles", 1, 6, 3)
        ph = st.empty()

        if "breath_running" not in ss:
            ss.breath_running = False
        cstart, cstop = st.columns(2)
        if cstart.button("Start", use_container_width=True):
            ss.breath_running = True
        if cstop.button("Stop", use_container_width=True):
            ss.breath_running = False

        def phase(label, sec):
            with ph.container():
                st.markdown(
                    f"<div class='pin-card center'><h3>{label}</h3><div class='muted'>{sec}s</div></div>",
                    unsafe_allow_html=True
                )
                pb = st.progress(0)
                for i in range(sec):
                    if not ss.breath_running:
                        return False
                    pb.progress(int((i + 1) / sec * 100))
                    time.sleep(1)
            return ss.breath_running

        if ss.breath_running:
            for _ in range(cycles):
                if mode == "4-7-8":
                    if not phase("Inhale", 4): break
                    if not phase("Hold", 7): break
                    if not phase("Exhale", 8): break
                else:
                    if not phase("Inhale", 4): break
                    if not phase("Hold", 4): break
                    if not phase("Exhale", 4): break
                    if not phase("Hold", 4): break
            ph.empty()
            if ss.breath_running:
                st.success("Nice work. Notice any shift?")
                ss.exercise_streak += 1
            ss.breath_running = False

    with t2:
        st.caption("Cognitive reframing: catch → check → change")
        ccol = st.columns(3)
        thought = ccol[0].text_area("Automatic Thought", height=120, placeholder="e.g., I always mess things up")
        evidence = ccol[1].text_area("Evidence For/Against", height=120, placeholder="For: ...\nAgainst: ...")
        alt = ccol[2].text_area("Balanced Alternative", height=120, placeholder="A more balanced way to say this is...")
        if st.button("Generate gentle reframe"):
            try:
                m = genai.GenerativeModel(MODEL)
                prompt = f"""You are a CBT-style coach. Given:
Automatic thought: {thought}
Evidence: {evidence}
Balanced alternative: {alt}
Return 3 short, compassionate reframes in bullet points."""
                r = m.generate_content(prompt, generation_config={"temperature": 0.6, "max_output_tokens": 250})
                txt = (getattr(r, "text", "") or "").strip()
            except Exception:
                txt = ("• Maybe the mistake says nothing about your worth.\n"
                       "• One moment doesn’t define all of you.\n"
                       "• What would you tell a close friend in this situation?")
            html_txt = txt.replace("- ", "• ").replace("\n", "<br>")
            st.markdown(f"<div class='pin-card'>{html_txt}</div>", unsafe_allow_html=True)

    with t3:
        st.caption("Quick resets for the nervous system")
        col = st.columns(2)
        if col[0].button("5-4-3-2-1"):
            st.info("5 see · 4 touch · 3 hear · 2 smell · 1 taste")
        if col[1].button("Progressive Muscle Relax"):
            st.info("Start at toes → tense 5s → release 10s → move upward.")


elif page == "🎮 Games":
    # -------------------- Minimal floating pink petals (page-local) --------------------
    st.markdown("""
    <style>
    .games-wrap{ position:relative; }
    .petal{ position:absolute; top:-20px; left:50%; width:10px; height:14px; background:#f7c3d0aa;
            border-radius:10px 10px 2px 10px; transform:rotate(15deg); animation:fall 8s linear infinite; filter:blur(.2px);}
    .petal.p2{ left:20%; animation-duration:9s; opacity:.7; transform:rotate(-10deg);}
    .petal.p3{ left:75%; animation-duration:10s; opacity:.55;}
    .petal.p4{ left:35%; animation-duration:11s; opacity:.5; transform:rotate(25deg);}
    @keyframes fall{ 0%{ transform:translateY(0) rotate(10deg);} 100%{ transform:translateY(600px) rotate(60deg);} }
    .card-grid{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-top:8px; }
    @media(max-width:1100px){ .card-grid{ grid-template-columns:repeat(2,1fr);} }
    @media(max-width:640px){ .card-grid{ grid-template-columns:1fr;} }
    .gcard{
        background: var(--panel); border:1px solid rgba(0,0,0,.06);
        border-radius: 18px; padding:14px; box-shadow: 0 10px 24px rgba(0,0,0,.08);
        transition: all .22s ease; position:relative; overflow:hidden;
    }
    .gcard:hover{ transform: translateY(-4px); box-shadow: 0 16px 36px rgba(211,107,138,.18); }
    .gcard .tag{ display:inline-block; padding:4px 8px; border-radius:999px; background:var(--accent-soft); font-size:.8rem; }
    .gcard h3{ margin:.4rem 0 .2rem 0; }
    .gcard .desc{ color:var(--muted); font-size:.9rem; min-height:40px; }
    .gcard .openbtn{ margin-top:8px; width:100%; padding:10px 12px; border-radius:12px; border:1px solid rgba(0,0,0,.06);
                     background:linear-gradient(135deg,#fff, var(--accent-soft)); cursor:pointer; font-weight:600; }
    .gcard .openbtn:hover{ filter:brightness(1.02); box-shadow:0 8px 22px rgba(0,0,0,.08);}
    .active-outline{ outline:2px solid #d36b8a88; }
    </style>
    """, unsafe_allow_html=True)

    # -------------------- Card Grid selector --------------------
    games = [
        {
            "key":"Reaction Focus",
            "tag":"speed",
            "title":"⚡ Reaction Focus",
            "desc":"Wait for GO, then tap instantly. Track best & average.",
        },
        {
            "key":"Even–Odd Blitz",
            "tag":"focus",
            "title":"🔢 Even–Odd Blitz",
            "desc":"See a number. Tap Even or Odd. 10 quick rounds.",
        },

        {
            "key":"Emotion Sort",
            "tag":"awareness",
            "title":"🌈 Emotion Sort",
            "desc":"Sort feeling-words into emotion bins. Gentle, reflective.",
        },
        {
            "key":"Affirmation Builder",
            "tag":"self-kindness",
            "title":"💖 Affirmation Builder",
            "desc":"Craft kind, personal affirmations. Save the ones you like.",
        },
    ]
    if "game_view" not in st.session_state:
        st.session_state.game_view = games[0]["key"]

    st.subheader("🎮 Play Zone")
    st.caption("Hover over a card — then click **Open** to play. (Rose Bento vibes with soft hover ✨)")
    st.markdown('<div class="games-wrap">', unsafe_allow_html=True)
    # petals
    st.markdown('<div class="petal"></div><div class="petal p2"></div><div class="petal p3"></div><div class="petal p4"></div>', unsafe_allow_html=True)

    # render grid
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, g in enumerate(games):
        with cols[i % 4]:
            active_cls = " active-outline" if st.session_state.game_view == g["key"] else ""
            st.markdown(f"<div class='gcard{active_cls}'>"
                        f"<span class='tag'>{g['tag']}</span>"
                        f"<h3>{g['title']}</h3>"
                        f"<div class='desc'>{g['desc']}</div>"
                        f"</div>", unsafe_allow_html=True)
            if st.button("Open", key=f"open_{g['key']}", use_container_width=True):
                st.session_state.game_view = g["key"]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)  # /card-grid
    st.markdown('</div>', unsafe_allow_html=True)  # /games-wrap

    st.write("---")

    # -------------------- Shared helpers / persistence --------------------
    def _save_games():
        try:
            save_games()
        except Exception:
            # fallback in case save_games not imported in your earlier context
            json.dump(ss.games, open(GAMES_JSON, "w"), indent=2)

    # Ensure games dict has new fields
    ss.games.setdefault("reaction", [])
    ss.games.setdefault("eo_best", 0)
    ss.games.setdefault("emotion_sort_best", 0)
    ss.games.setdefault("affirmations_saved", [])

        # ==================== GAME 1: Reaction Focus ====================
    if st.session_state.game_view == "Reaction Focus":
        st.subheader("⚡ Reaction Focus")
        st.caption("When it says **GO!**, hit the button immediately. Try to beat your best.")
        if "rf_phase" not in ss:
            ss.rf_phase=None; ss.rf_delay=0.0; ss.rf_set=0.0; ss.rf_go=0.0

        c1, c2 = st.columns([1,1])
        if ss.rf_phase is None:
            if c1.button("Start ▶️", key="rf_start", use_container_width=True):
                ss.rf_phase="wait"; ss.rf_delay=random.uniform(1.6, 3.8); ss.rf_set=time.time(); st.rerun()
            c2.button("Reset ⟲", key="rf_reset_disabled", use_container_width=True, disabled=True)
            st.info("Press **Start** and… wait. Don’t click until you see **GO!**.")
        elif ss.rf_phase == "wait":
            if c2.button("Reset ⟲", key="rf_reset", use_container_width=True):
                ss.rf_phase=None; st.rerun()
            remain = time.time() - ss.rf_set
            if remain >= ss.rf_delay:
                ss.rf_phase="go"; ss.rf_go=time.time(); st.rerun()
            else:
                st.warning("⏳ Wait for **GO!** …")
                time.sleep(0.2); st.rerun()
        elif ss.rf_phase == "go":
            st.success("**GO!** Tap now!")
            if st.button("Click!", key="rf_click", use_container_width=True):
                rt = round((time.time()-ss.rf_go)*1000)
                ss.games["reaction"].append(rt); _save_games()
                ss.rf_phase=None
                st.success(f"Your reaction time: **{rt} ms**")

        rx = ss.games.get("reaction", [])
        if rx:
            best=min(rx); avg=sum(rx)/len(rx)
            st.markdown(f"- Best: **{best:.0f} ms** • Avg: **{avg:.0f} ms** • Plays: {len(rx)}")
            if st.button("Clear scores", key="rf_clear", type="secondary"):
                ss.games["reaction"] = []; _save_games(); st.success("Cleared.")

    # ==================== GAME 2: Even–Odd Blitz (replacing Stroop) ====================
    elif st.session_state.game_view == "Even–Odd Blitz":
        st.subheader("🔢 Even–Odd Blitz")
        st.caption("You’ll see a number. Tap **Even** or **Odd**. 10 rounds — quick focus!")

        # init state
        if "eo_phase" not in ss:
            ss.eo_phase = "idle"          # idle → showing → answered → done
            ss.eo_round = 0
            ss.eo_score = 0
            ss.eo_current = None          # current integer

        def new_number():
            ss.eo_current = random.randint(1, 99)
            ss.eo_phase = "showing"

        top = st.columns([2,1])
        if top[0].button("Start / Next ▶️", key="eo_next", use_container_width=True):
            if ss.eo_phase in ("idle", "answered", "done"):
                if ss.eo_round >= 10:
                    # finished -> store best then reset for a fresh run
                    ss.games["eo_best"] = int(max(ss.games.get("eo_best", 0), ss.eo_score))
                    _save_games()
                    ss.eo_round = 0
                    ss.eo_score = 0
                ss.eo_round += 1
                new_number()
                st.rerun()

        if top[1].button("Reset ⟲", key="eo_reset", use_container_width=True):
            ss.eo_phase, ss.eo_round, ss.eo_score = "idle", 0, 0
            ss.eo_current = None
            st.rerun()

        # show current number
        if ss.eo_phase == "showing" and ss.eo_current is not None:
            n = ss.eo_current
            st.markdown(
                f"<div class='pin-card' style='text-align:center;'>"
                f"<div style='font-size:54px;font-weight:800;letter-spacing:.5px'>{n}</div>"
                f"<div class='muted'>Round {ss.eo_round}/10</div>"
                f"</div>", unsafe_allow_html=True
            )

            c1, c2 = st.columns(2)
            picked = None
            if c1.button("Even", key=f"eo_even_{ss.eo_round}", use_container_width=True): picked = "even"
            if c2.button("Odd",  key=f"eo_odd_{ss.eo_round}",  use_container_width=True): picked = "odd"

            if picked and ss.eo_phase == "showing":  # count only once
                correct = ("even" if n % 2 == 0 else "odd")
                ss.eo_phase = "answered"
                if picked == correct:
                    ss.eo_score += 1
                    st.success("Correct ✓")
                else:
                    st.error(f"Oops — it was **{correct.title()}**")
                _save_games()

        # wrap-up / next
        if ss.eo_phase == "answered":
            if ss.eo_round >= 10:
                best = max(ss.games.get("eo_best", 0), ss.eo_score)
                ss.games["eo_best"] = int(best); _save_games()
                st.markdown(f"### 🎯 Final Score: **{ss.eo_score}/10** • Best: **{best}/10**")
                st.balloons()
                ss.eo_phase = "done"
            else:
                st.info("Press **Next ▶️** for the next number.")

        if ss.eo_round and ss.eo_round <= 10:
            st.markdown(f"**Score:** {ss.eo_score} / {ss.eo_round}")

    # ==================== GAME 3: Emotion Sort (card → bin) ====================
    elif st.session_state.game_view == "Emotion Sort":
        st.subheader("🌈 Emotion Sort")
        st.caption("Sort each feeling-word into the best fitting bin: **Happy**, **Sad**, **Anxious**. Reflect after you submit.")

        EMO_MAP = {
            "joyful":"Happy","grateful":"Happy","hopeful":"Happy","proud":"Happy","calm":"Happy","content":"Happy",
            "down":"Sad","lonely":"Sad","blue":"Sad","disappointed":"Sad","gloomy":"Sad","drained":"Sad",
            "worried":"Anxious","restless":"Anxious","nervous":"Anxious","tense":"Anxious","overwhelmed":"Anxious","panicky":"Anxious",
        }
        WORDS = list(EMO_MAP.keys())

        # init state
        if "es_pool" not in ss:
            sample = random.sample(WORDS, 9)  # 9 words per round
            ss.es_pool = sample
            ss.es_bins = {"Happy":[], "Sad":[], "Anxious":[]}
            ss.es_done = False
            ss.es_score = None

        st.markdown("**Words:**")
        chip_cols = st.columns(3)
        for i,w in enumerate(ss.es_pool):
            with chip_cols[i%3]:
                cols2 = st.columns([2,1,1,1])
                cols2[0].markdown(f"<div class='chip' style='display:inline-block;padding:6px 10px;border-radius:999px;background:var(--accent-soft);margin:4px 0'>{w}</div>", unsafe_allow_html=True)
                if cols2[1].button("😊", key=f"es_h_{i}", help="Happy"):
                    ss.es_bins["Happy"].append(w); ss.es_pool.remove(w); st.rerun()
                if cols2[2].button("😔", key=f"es_s_{i}", help="Sad"):
                    ss.es_bins["Sad"].append(w); ss.es_pool.remove(w); st.rerun()
                if cols2[3].button("😬", key=f"es_a_{i}", help="Anxious"):
                    ss.es_bins["Anxious"].append(w); ss.es_pool.remove(w); st.rerun()

        st.write("")
        bcols = st.columns(3)
        for j,binname in enumerate(["Happy","Sad","Anxious"]):
            with bcols[j]:
                st.markdown(f"**{binname}**")
                if ss.es_bins[binname]:
                    st.markdown(", ".join([f"`{x}`" for x in ss.es_bins[binname]]))
                else:
                    st.markdown("<span class='muted'>— empty —</span>", unsafe_allow_html=True)

        st.write("")
        c1,c2,c3 = st.columns(3)
        if c1.button("Submit"):
            score = 0
            total = sum(len(v) for v in ss.es_bins.values())
            for wlist in ss.es_bins.values():
                for w in wlist:
                    if EMO_MAP[w] in [k for k,v in ss.es_bins.items() if w in v]:
                        score += 1
            ss.es_score = (score, total)
            ss.es_done = True
        if c2.button("Reset Round"):
            ss.es_pool=[]; ss.es_bins={"Happy":[], "Sad":[], "Anxious":[]}; ss.es_done=False; ss.es_score=None
            st.rerun()
        if c3.button("New Round"):
            sample = random.sample(WORDS, 9)
            ss.es_pool = sample; ss.es_bins={"Happy":[], "Sad":[], "Anxious":[]}; ss.es_done=False; ss.es_score=None
            st.rerun()

        if ss.es_done and ss.es_score is not None:
            got, total = ss.es_score
            st.success(f"Score: **{got}/{total}**")
            if got == total: st.balloons()
            ss.games["emotion_sort_best"] = max(ss.games.get("emotion_sort_best",0), got)
            _save_games()
            with st.expander("Reflect (optional)"):
                txt = st.text_area("What did you notice about these emotions?")
                if st.button("Save as note to gratitude"):
                    ss.gratitude.append(f"{time.strftime('%Y-%m-%d')}: Reflection — {txt.strip()}")
                    save_gratitude()
                    st.success("Saved to gratitude.json")

            st.markdown(f"_Best this profile: **{ss.games['emotion_sort_best']}**_")

    # ==================== GAME 4: Affirmation Builder ====================
    elif st.session_state.game_view == "Affirmation Builder":
        st.subheader("💖 Affirmation Builder")
        st.caption("Compose a kind sentence about yourself. Keep it short and believable.")

        colA, colB, colC = st.columns(3)
        with colA:
            trait = st.selectbox("Pick a strength", ["resilient","kind","hard-working","curious","patient","brave","creative"])
        with colB:
            focus = st.selectbox("Focus area", ["self-worth","anxiety","motivation","study focus","social ease","sleep"])
        with colC:
            tone = st.selectbox("Tone", ["gentle","encouraging","matter-of-fact","hopeful"])

        situation = st.text_input("Optional situation (e.g., 'when exams feel heavy')")
        starter = f"I am {trait}, and I can handle this with {tone} steps"
        target = st.text_area("Draft (edit if you like)", value=starter, height=90)

        c1,c2,c3 = st.columns(3)
        made = None
        if c1.button("Generate suggestion"):
            try:
                m = genai.GenerativeModel(MODEL)
                prompt = f"Write one short {tone} affirmation for {focus}. Include the strength '{trait}'. Situation: {situation or '—'}"
                r = m.generate_content(prompt, generation_config={"temperature":0.7,"max_output_tokens":60})
                made = (getattr(r,"text","") or "").strip()
            except Exception:
                made = f"Even when {situation or 'things are tough'}, I remember I am {trait}, and I can take one small step at a time."
            st.markdown(f"<div class='pin-card'>{made}</div>", unsafe_allow_html=True)

        if c2.button("Save my draft"):
            af = target.strip()
            if af:
                ss.games["affirmations_saved"].append({"text":af, "ts":time.strftime("%Y-%m-%d %H:%M")})
                _save_games()
                st.success("Saved ✓  (see below)")

        if c3.button("Add to Gratitude"):
            af = (made or target).strip()
            if af:
                ss.gratitude.append(f"{time.strftime('%Y-%m-%d')}: {af}")
                save_gratitude()
                st.success("Added to gratitude wall ✓")

        if ss.games.get("affirmations_saved"):
            st.markdown("### Saved affirmations")
            for a in reversed(ss.games["affirmations_saved"][-8:]):
                st.markdown(f"- _{a['ts']}_ — **{a['text']}**")

elif page == "🎵 Music":
    # ==================== 🎧 Moody Melody (simple layout with image) ====================
    st.subheader("Moody Melody")

    # --- ensure structure ---
    ss.melody.setdefault("playlists", {"Calm Mix": []})
    ss.melody.setdefault("current", "Calm Mix")
    playlists = ss.melody["playlists"]
    if not playlists:
        playlists["Calm Mix"] = []
    current = ss.melody.get("current", "Calm Mix")
    if current not in playlists:
       current = list(playlists.keys())[0]
    ss.melody["current"] = current

    # --- playlist tabs ---
    tab_labels = list(playlists.keys())
    tabs = st.tabs(tab_labels + ["➕ New"])
    tab_map = {lbl: t for lbl, t in zip(tab_labels, tabs)}

    for lbl, t in tab_map.items():
       with t:
         if current != lbl:
             ss.melody["current"] = lbl
             current = lbl

    # --- New / Rename / Delete controls ---
    with tabs[-1]:
       new_name = st.text_input("New playlist name", placeholder="e.g., Rainy Night Focus")
       if st.button("Create playlist"):
           name = (new_name or "").strip()
           if not name:
               st.warning("Please enter a name.")
           elif name in playlists:
               st.warning("A playlist with that name exists.")
           else:
               playlists[name] = []
               ss.melody["current"] = name
               save_melody()
               st.success(f"Created **{name}**")
               st.rerun()

    with tab_map[current]:
       # Header row: name + rename + delete
       r1c1, r1c2, r1c3 = st.columns([2,1,1])
       r1c1.markdown(f"### {current}")
       new_title = r1c2.text_input("Rename", value=current, label_visibility="collapsed", key="mm_rename_simple")
       if r1c2.button("Rename"):
            nt = (new_title or "").strip()
            if nt and nt != current and nt not in playlists:
                playlists[nt] = playlists.pop(current)
                ss.melody["current"] = nt
                save_melody()
                st.success("Renamed ✓")
                st.rerun()
            else:
                st.warning("Pick a new, unique name.")
       if r1c3.button("Delete") and len(playlists) > 1:
           playlists.pop(current, None)
           ss.melody["current"] = list(playlists.keys())[0]
           save_melody()
           st.success("Deleted ✓")
           st.rerun()

    st.markdown("---")

    # ---------- SIDE BY SIDE: Add a track (left) + Music Image (right) ----------
    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        st.markdown("#### Add a track")
        a1, a2, a3 = st.columns([2, 3, 1])
        with a1:
           t_title = st.text_input("Title", placeholder="lofi rain on windows")
        with a2:
           t_url = st.text_input("Link (YouTube/Spotify/MP3)", placeholder="https://...")
        with a3:
           t_mood = st.selectbox("Mood", ["calm", "focus", "sleep", "uplift", "breath"], index=0)

        c_add1, c_add2 = st.columns([1, 1])
        if c_add1.button("➕ Add link"):
           if not t_url.strip():
              st.warning("Paste a link first.")
           else:
              title = t_title.strip() or "Untitled"
              playlists[current].append({
                  "title": title, "mood": t_mood, "src": "url",
                   "path": "", "url": t_url.strip(),
                   "added": time.strftime("%Y-%m-%d %H:%M")
              })
              save_melody(); st.success("Added ✓"); st.rerun()

        up = c_add2.file_uploader("…or upload audio", type=["mp3", "wav", "ogg", "m4a"], label_visibility="collapsed")
        if up is not None and st.button("📤 Upload file"):
            ext = Path(up.name).suffix.lower()
            safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", Path(up.name).stem) + ext
            local_path = (AUDIO_DIR / safe)
            with open(local_path, "wb") as f:
               f.write(up.read())
            title = t_title.strip() or Path(up.name).stem
            playlists[current].append({
               "title": title, "mood": t_mood, "src": "local",
               "path": str(local_path), "url": "",
               "added": time.strftime("%Y-%m-%d %H:%M")
            })
            save_melody(); st.success("Uploaded ✓"); st.rerun()

    with right_col:
        # Pretty image on the right
        music_image = "assets/music_switch.jpeg"  # ensure this file exists
        if os.path.exists(music_image):
           st.image(music_image, caption="music: ON • world: OFF", use_column_width=True)
        else:
           st.info("Add your image as assets/music_switch.jpeg")

    st.markdown("---")

    # ---------- Your Playlists (moved to bottom) ----------
    st.markdown("### 🎵 Your Playlists")

    if not playlists:
        st.info("No playlists yet. Create one using the ➕ tab above.")
    else:
        for pname, tracks in playlists.items():
           st.markdown(
              f"<div style='margin-top:10px;padding:10px 0;'>"
              f"<h4 style='margin-bottom:4px;color:#b14e72;'>{pname}</h4>"
              "</div>", unsafe_allow_html=True
            )
           if not tracks:
               st.caption("No songs yet. Add tracks above.")
           else:
               for idx, t in enumerate(tracks):
                   with st.container():
                      c1, c2, c3 = st.columns([4, 2, 1])
                      c1.markdown(f"**🎧 {t.get('title','Untitled')}**  ·  _{t.get('mood','')}_")
                      if t.get("src") == "local" and t.get("path"):
                          c2.audio(t["path"])
                      elif t.get("url"):
                          c2.link_button("Open Link", t["url"])
                      else:
                          c2.caption("—")
                      if c3.button("✖", key=f"mm_del_{pname}_{idx}"):
                          tracks.pop(idx)
                          save_melody()
                          st.rerun()

    st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)



elif page == "📈 Progress":
    st.subheader("Your Progress")
    df = ss.journal_df

    # --- Chart 1: Mood Trend ---
    if not df.empty and "mood_1to5" in df.columns:
        d2 = df.dropna(subset=["mood_1to5"]).copy()
        if not d2.empty:
            d2["#"] = range(1, len(d2) + 1)
            fig = px.line(
                d2, x="#", y="mood_1to5", markers=True, title="Mood Trend",
                range_y=[0, 5], color_discrete_sequence=["#227b79"]
            )
            fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, use_container_width=True)

    # --- Chart 2: Emotion Frequency ---
    if not df.empty and "emotion" in df.columns:
        counts = df["emotion"].value_counts().reset_index()
        counts.columns = ["emotion", "count"]
        if not counts.empty:
            fig2 = px.bar(
                counts, x="emotion", y="count", title="Emotion Frequency",
                color_discrete_sequence=["#f7b8d4"]
            )
            fig2.update_layout(margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig2, use_container_width=True)

    # --- Mood Calendar (last 31 days) ---
    st.subheader("Mood Calendar (last 31 days)")
    if not df.empty and "mood_1to5" in df.columns and "date" in df.columns:
        d3 = df.dropna(subset=["mood_1to5"]).copy()
        # parse dates safely and keep the most recent 31 entries
        d3["date"] = pd.to_datetime(d3["date"], errors="coerce")
        d3 = d3.dropna(subset=["date"]).sort_values("date").tail(31)

        if not d3.empty:
            # color map for moods 1..5
            mood_colors = {
                1: "#f8c6d8",  # light pink
                2: "#f6a8c6",
                3: "#f08fb5",
                4: "#c5e7d9",  # light green
                5: "#9adbc9"
            }

            cells = []
            for _, r in d3.iterrows():
                try:
                    m = int(r["mood_1to5"])
                except Exception:
                    m = 0
                color = mood_colors.get(m, "#eeeeee")
                date_str = r["date"].date().isoformat()
                cells.append(
                    f"<div title='{date_str} • mood {m}' "
                    f"style='width:22px;height:22px;border-radius:6px;background:{color};"
                    f"display:inline-block;margin:2px'></div>"
                )

            st.markdown(
                "<div class='pin-card' style='text-align:center'>" + "".join(cells) + "</div>",
                unsafe_allow_html=True
            )
        else:
            st.info("No recent mood entries to show on the calendar yet.")

    # --- Export / Download ---
    st.subheader("Export / Download")
    col = st.columns(3)
    col[0].download_button(
        "Download journal.csv",
        data=JOURNAL_CSV.read_bytes() if JOURNAL_CSV.exists() else b"",
        file_name=f"journal_{USER_ID}.csv"
    )
    col[1].download_button(
        "Download habits.csv",
        data=HABITS_CSV.read_bytes() if HABITS_CSV.exists() else b"",
        file_name=f"habits_{USER_ID}.csv"
    )
    col[2].download_button(
        "Download gratitude.json",
        data=GRATITUDE_JSON.read_bytes() if GRATITUDE_JSON.exists() else b"",
        file_name=f"gratitude_{USER_ID}.json"
    )

elif page == "⚙️ Settings":
    st.subheader("Appearance")
    st.caption("Switch themes in the sidebar under “🎨 Theme”.")
    st.subheader("Privacy")
    st.write("• Your data is stored under a per-user folder on this machine:")
    st.code(str(USER_DIR))
    st.write("• Change the name/PIN in sidebar to switch profiles.")
    st.write("• For a multi-user cloud deployment, we can add authentication + DB (SQLite/Postgres).")

    st.subheader("Danger Zone")
    if st.button("Delete my local data"):
        try:
            deleted_path = str(USER_DIR.resolve())
            if USER_DIR.exists():
                shutil.rmtree(USER_DIR)
            for k in list(st.session_state.keys()):
                if k != "_nav":
                    del st.session_state[k]
            st.success(f"Deleted all data under: {deleted_path}. The app will reset.")
            st.rerun()
        except Exception as e:
            st.error("Could not delete: " + str(e))
