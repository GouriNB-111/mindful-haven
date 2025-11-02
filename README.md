# 🌸 Mindful Haven — A Gentle Space for Calm & Reflection 🧠

> _“It’s okay to not be okay.”_  
> A soothing, per-user Streamlit app for journaling, reflection, nutrition, games & mindfulness tools — powered by **Gemini AI**.

![Poster](assets/poster_okay.png)

---

## ✨ Overview

**Mindful Haven** is a warm, privacy-friendly app that helps you:
- Reflect on your emotions
- Build calming habits
- Track nutrition & hydration
- Play mini focus games
- Chat safely with an AI that listens — not diagnoses 🌷

It’s designed with Pinterest-inspired visuals, soft gradients, and per-user local data isolation.

---

## 🌿 Key Features

### 🧠 Core Highlights
- 👤 **Private Profiles:** Enter your name + optional PIN → app creates a unique data folder (local per-user storage).
- 🎨 **Beautiful Themes:** “Rose Bento (pink)” & “Sage Calm (green)” — cozy cards, shadows, and smooth gradients.
- ⚠️ **Built-in Safety:** Detects crisis keywords and displays India helplines automatically.

---

### 💬 **Chat (Gemini-powered)**
- Gentle AI support that validates feelings and provides grounding suggestions.
- Crisis detection phrases trigger helpline display.
- Avoids excessive API calls to reduce 429 quota errors.

---

### 📓 **Journal**
- 4 short reflection prompts + mood slider (1–5).
- Search, filter, and see your **reflection streaks** 🌱 🌿 🌸 🌷 💮.
- “Prompt of the day” for quick inspiration.

---

### 🍎 **Nutrition Tracker**
- Log daily meals, hydration (12-glass tracker), macros, and notes.
- Weekly checklist: Fruits, Veggies, No Sugary Drinks.
- **7-day visual trend**: calories or hydration bar chart.
- CSV export for offline storage.

---

### 🧩 **Wellness Tools**
- 🫁 **Breathing Timer:** 4-7-8 or Box (4-4-4-4) with animated progress.
- 🧠 **CBT Reframe:** Catch → Check → Change (AI or safe fallback suggestions).
- 🌿 **Grounding:** 5-4-3-2-1 sensory reset & muscle relaxation.

---

### 🎮 **Mini-Games**
- ⚡ **Reaction Focus:** Tap instantly after “GO!” — tracks your best reaction time.  
- 🔢 **Even–Odd Blitz:** Quick 10 rounds of focus-speed fun.  
- 🌈 **Emotion Sort:** Sort emotion words into Happy, Sad, Anxious — with reflection notes.  
- 💖 **Affirmation Builder:** Create & save kind affirmations. Add to Gratitude Wall.

---

### 🎵 **Moody Melody (Music Zone)**
- Build mini playlists from links or upload local MP3/WAV files.
- Calm, focus, and sleep mixes — “music: ON • world: OFF”.

---

### 📈 **Progress Dashboard**
- Mood trend chart (Plotly line)
- Emotion frequency bar chart
- 31-day mood calendar (color-coded by rating)
- One-click export of journal, habits, and gratitude data

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend/UI** | Streamlit + Custom CSS (Google Fonts, gradients, cards) |
| **AI Engine** | Google Gemini via `google-generativeai` |
| **Data & Viz** | Pandas, Plotly Express |
| **State/Storage** | Streamlit `session_state`, local CSV/JSON (per-user) |

---

## 📦 Project Structure

### 🗂️ **Project Structure**

```plaintext
mindful-haven/
├─ assets/                    # app visuals & icons
│  ├─ logo_primary.png
│  ├─ music_switch.jpeg
│  ├─ nutrition_banner.jpeg
│  ├─ nutrition_side.jpeg
│  └─ poster_okay.png
│
├─ data/                      # runtime: per-user folders & files (auto-created)
│  ├─ <user_hash>/journal.csv
│  ├─ <user_hash>/gratitude.json
│  ├─ <user_hash>/habits.csv
│  └─ ...
│
├─ .streamlit/
│  └─ config.toml             # Streamlit theme + page config
│
├─ mental_health.py           # main Streamlit app (entry point)
└─ requirements.txt           # Python dependencies


### Clone the repository
```bash
git clone https://github.com/GouriNB-111/mindful-haven.git
cd mindful-haven



