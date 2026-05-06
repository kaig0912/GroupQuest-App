import streamlit as st
from datetime import datetime

st.set_page_config(page_title="GroupQuest", page_icon="🏆", layout="centered")

# --- minimal styling ---
st.markdown("""
<style>
    .block-container { max-width: 680px; padding-top: 2rem; }
    h1, h2, h3 { font-weight: 700; }
    .tag {
        display: inline-block;
        background: #f0f0f0;
        color: #444;
        font-size: 0.72rem;
        padding: 2px 10px;
        border-radius: 99px;
        margin-right: 4px;
    }
    hr { border: none; border-top: 1px solid #eee; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# --- session state ---
if "challenges" not in st.session_state:
    st.session_state.challenges = [
        {"id": 1, "title": "30 Tage früh aufstehen", "desc": "Jeden Tag vor 7 Uhr aufstehen.", "category": "Mindset", "days": 30, "members": ["Jana", "Tom", "Sara"], "checkins": []},
        {"id": 2, "title": "Täglich 20 Min lesen", "desc": "Ein Buch pro Monat durchlesen.", "category": "Bildung", "days": 30, "members": ["Lena", "Max"], "checkins": []},
        {"id": 3, "title": "Kein Junk Food diese Woche", "desc": "7 Tage kein Fast Food.", "category": "Ernährung", "days": 7, "members": ["Jana", "Alex", "Tom"], "checkins": []},
    ]
if "username" not in st.session_state:
    st.session_state.username = ""
if "feed" not in st.session_state:
    st.session_state.feed = [
        {"user": "Jana", "challenge": "30 Tage früh aufstehen", "text": "Tag 5 ✅ War nicht einfach heute aber hab's geschafft!", "time": "vor 1h"},
        {"user": "Lena", "challenge": "Täglich 20 Min lesen", "text": "Atomic Habits Kapitel 4 durch 📚", "time": "vor 3h"},
        {"user": "Tom", "challenge": "Kein Junk Food diese Woche", "text": "Smoothie statt Burger 🥤", "time": "vor 5h"},
    ]

# --- login ---
if not st.session_state.username:
    st.title("🎯 GroupQuest")
    st.write("Gemeinsam Challenges angehen.")
    st.divider()
    name = st.text_input("Wie heißt du?")
    if st.button("Loslegen →") and name.strip():
        st.session_state.username = name.strip()
        st.rerun()
    st.stop()

# --- header ---
user = st.session_state.username
st.markdown(f"### 🏆 GroupQuest &nbsp; <span style='font-size:.85rem;color:#999;font-weight:400'>Hi, {user} 👋</span>", unsafe_allow_html=True)
st.divider()

# --- tabs ---
tab1, tab2, tab3 = st.tabs(["Challenges", "Feed", "Erstellen"])


# ── TAB 1: CHALLENGES ──────────────────────────────
with tab1:
    for c in st.session_state.challenges:
        is_member = user in c["members"]

        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{c['title']}**")
                st.caption(c["desc"])
                st.markdown(
                    f'<span class="tag">{c["category"]}</span>'
                    f'<span class="tag">⏳ {c["days"]} Tage</span>'
                    f'<span class="tag">👥 {len(c["members"])}</span>'
                    f'<span class="tag">✅ {len(c["checkins"])} Check-ins</span>',
                    unsafe_allow_html=True
                )
            with col2:
                if is_member:
                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.popover("Check-in"):
                        text = st.text_area("Was hast du heute gemacht?", key=f"ci_{c['id']}", height=80)
                        if st.button("Einreichen", key=f"btn_ci_{c['id']}"):
                            if text.strip():
                                c["checkins"].append({"user": user, "text": text, "time": "gerade"})
                                st.session_state.feed.insert(0, {
                                    "user": user,
                                    "challenge": c["title"],
                                    "text": text,
                                    "time": "gerade eben"
                                })
                                st.success("Gespeichert! ✅")
                                st.rerun()
                else:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Beitreten", key=f"join_{c['id']}"):
                        c["members"].append(user)
                        st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)


# ── TAB 2: FEED ────────────────────────────────────
with tab2:
    if not st.session_state.feed:
        st.write("Noch keine Posts. Mach einen Check-in!")
    for post in st.session_state.feed:
        st.markdown(f"**{post['user']}** · *{post['challenge']}* · <span style='color:#aaa;font-size:.8rem'>{post['time']}</span>", unsafe_allow_html=True)
        st.write(post["text"])
        st.markdown("<hr>", unsafe_allow_html=True)


# ── TAB 3: ERSTELLEN ───────────────────────────────
with tab3:
    st.markdown("**Neue Challenge**")
    title = st.text_input("Name der Challenge")
    desc  = st.text_area("Beschreibung (klare Regeln!)", height=80)
    cat   = st.selectbox("Kategorie", ["Fitness", "Bildung", "Ernährung", "Mindset"])
    days  = st.slider("Dauer in Tagen", 3, 90, 30)

    if st.button("Challenge erstellen 🚀"):
        if title.strip() and desc.strip():
            new_id = len(st.session_state.challenges) + 1
            st.session_state.challenges.append({
                "id": new_id,
                "title": title,
                "desc": desc,
                "category": cat,
                "days": days,
                "members": [user],
                "checkins": [],
            })
            st.success(f"'{title}' wurde erstellt! Du bist automatisch dabei. ✅")
            st.rerun()
        else:
            st.warning("Titel und Beschreibung ausfüllen!")