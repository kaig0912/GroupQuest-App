import streamlit as st
from datetime import datetime

st.set_page_config(page_title="GroupQuest", page_icon="🏆", layout="centered")

# --- minimal styling ---
st.markdown("""
<style>
    .block-container { max-width: 680px; padding-top: 2rem; }
    .stButton > button { min-width: 90px; }
    h1, h2, h3 { font-weight: 700; }
    .tag {
        display: inline-block;
        background: rgba(128, 128, 128, 0.16);
        color: inherit;
        font-size: 0.72rem;
        padding: 3px 10px;
        border-radius: 99px;
        margin: 3px 4px 3px 0;
    }
    .muted { opacity: .72; font-size: .9rem; margin-bottom: .15rem; }
    .empty-box {
        background: rgba(128, 128, 128, 0.08);
        border: 1px dashed rgba(128, 128, 128, 0.35);
        border-radius: 12px;
        padding: 1rem;
        opacity: .8;
    }
    hr { border: none; border-top: 1px solid #eee; margin: 1.5rem 0; }
    div[data-testid="stHorizontalBlock"] { gap: .8rem; }
</style>
""", unsafe_allow_html=True)

# --- session state ---
if "challenges" not in st.session_state:
    st.session_state.challenges = [
        {"id": 1, "title": "30 Tage früh aufstehen", "desc": "Jeden Tag vor 7 Uhr aufstehen.", "category": "Mindset", "days": 30, "goal": "Bessere Morgenroutine aufbauen", "members": ["Jana", "Tom", "Sara"], "checkins": [], "progress": 5, "creator": "Jana"},
        {"id": 2, "title": "Täglich 20 Min lesen", "desc": "Ein Buch pro Monat durchlesen.", "category": "Bildung", "days": 30, "goal": "Konstant lernen statt nur nebenbei konsumieren", "members": ["Lena", "Max"], "checkins": [], "progress": 4, "creator": "Lena"},
        {"id": 3, "title": "Kein Junk Food diese Woche", "desc": "7 Tage kein Fast Food.", "category": "Ernährung", "days": 7, "goal": "Bewusster essen und weniger impulsiv snacken", "members": ["Jana", "Alex", "Tom"], "checkins": [], "progress": 3, "creator": "Alex"},
    ]
if "username" not in st.session_state:
    st.session_state.username = ""
if "feed" not in st.session_state:
    st.session_state.feed = [
        {"id": 1, "user": "Jana", "challenge": "30 Tage früh aufstehen", "text": "Tag 5 ✅ War nicht einfach heute aber hab's geschafft!", "time": "vor 1h", "reactions": {}, "comments": []},
        {"id": 2, "user": "Lena", "challenge": "Täglich 20 Min lesen", "text": "Atomic Habits Kapitel 4 durch 📚", "time": "vor 3h", "reactions": {}, "comments": []},
        {"id": 3, "user": "Tom", "challenge": "Kein Junk Food diese Woche", "text": "Smoothie statt Burger 🥤", "time": "vor 5h", "reactions": {}, "comments": []},
    ]
if "created_message" not in st.session_state:
    st.session_state.created_message = ""
if "xp" not in st.session_state:
    st.session_state.xp = {}
if "next_post_id" not in st.session_state:
    st.session_state.next_post_id = 4

if "checkin_message" not in st.session_state:
    st.session_state.checkin_message = ""

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
user_xp = st.session_state.xp.get(user, 0)
st.markdown("### 🏆 GroupQuest")
st.caption(f"Hi, {user} 👋 · {user_xp} XP")
if st.button("Logout", key="logout_button"):
    st.session_state.username = ""
    st.rerun()
st.divider()

# --- tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Challenges", "Feed", "Erstellen", "Meine Fortschritte", "Leaderboard"])


# ── TAB 1: CHALLENGES ──────────────────────────────
with tab1:
    if st.session_state.checkin_message:
        st.success(st.session_state.checkin_message)
        st.session_state.checkin_message = ""
    search = st.text_input("Challenge suchen", placeholder="z. B. lesen, Fitness, Ernährung ...")
    selected_category = st.selectbox("Kategorie filtern", ["Alle", "Fitness", "Bildung", "Ernährung", "Mindset"])

    visible_challenges = []
    for challenge in st.session_state.challenges:
        search_term = search.strip().lower()
        matches_search = search_term in challenge["title"].lower() or search_term in challenge["desc"].lower() or search_term in challenge["goal"].lower()
        matches_category = selected_category == "Alle" or challenge["category"] == selected_category
        if matches_search and matches_category:
            visible_challenges.append(challenge)

    if not visible_challenges:
        st.markdown("<div class='empty-box'>Keine passende Challenge gefunden.</div>", unsafe_allow_html=True)

    for c in visible_challenges:
        is_member = user in c["members"]

        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{c['title']}**")
                st.caption(c["desc"])
                st.markdown(f"<div class='muted'>Ziel: {c['goal']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='muted'>Teilnehmer: {', '.join(c['members'])}</div>", unsafe_allow_html=True)
                progress_value = min(c.get("progress", 0) / max(c["days"], 1), 1)
                st.progress(progress_value)
                st.markdown(
                    f'<span class="tag">{c["category"]}</span>'
                    f'<span class="tag">⏳ {c["days"]} Tage</span>'
                    f'<span class="tag">📈 Tag {min(c.get("progress", 0), c["days"])} von {c["days"]}</span>'
                    f'<span class="tag">👥 {len(c["members"])}</span>'
                    f'<span class="tag">✅ {len(c["checkins"])} Check-ins</span>',
                    unsafe_allow_html=True
                )
                if c.get("creator") == user:
                    with st.expander("Challenge bearbeiten"):
                        with st.form(f"edit_challenge_{c['id']}"):
                            edited_title = st.text_input("Name", value=c["title"], key=f"edit_title_{c['id']}")
                            edited_desc = st.text_area("Beschreibung", value=c["desc"], key=f"edit_desc_{c['id']}")
                            edited_goal = st.text_input("Ziel", value=c["goal"], key=f"edit_goal_{c['id']}")
                            edited_category = st.selectbox(
                                "Kategorie",
                                ["Fitness", "Bildung", "Ernährung", "Mindset"],
                                index=["Fitness", "Bildung", "Ernährung", "Mindset"].index(c["category"]),
                                key=f"edit_category_{c['id']}"
                            )
                            edited_days = st.slider("Dauer in Tagen", 3, 90, c["days"], key=f"edit_days_{c['id']}")
                            save_changes = st.form_submit_button("Änderungen speichern")

                        if save_changes:
                            if edited_title.strip() and edited_desc.strip() and edited_goal.strip():
                                c["title"] = edited_title.strip()
                                c["desc"] = edited_desc.strip()
                                c["goal"] = edited_goal.strip()
                                c["category"] = edited_category
                                c["days"] = edited_days
                                c["progress"] = min(c.get("progress", 0), edited_days)
                                st.success("Challenge wurde aktualisiert.")
                                st.rerun()
                            else:
                                st.warning("Name, Beschreibung und Ziel dürfen nicht leer sein.")

                        if st.button("Challenge löschen", key=f"delete_challenge_{c['id']}"):
                            st.session_state.challenges = [challenge for challenge in st.session_state.challenges if challenge["id"] != c["id"]]
                            st.session_state.feed = [post for post in st.session_state.feed if post.get("challenge") != c["title"]]
                            st.rerun()
            with col2:
                if is_member:
                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.popover("Check-in"):
                        with st.form(f"checkin_form_{c['id']}", clear_on_submit=True):
                            text = st.text_area("Was hast du heute gemacht?", key=f"ci_{c['id']}", height=80)
                            submitted_checkin = st.form_submit_button("Einreichen")

                        if submitted_checkin:
                            if text.strip():
                                clean_text = text.strip()
                                c["checkins"].append({"user": user, "text": clean_text, "time": datetime.now().strftime("%d.%m.%Y %H:%M")})
                                c["progress"] = min(c.get("progress", 0) + 1, c["days"])
                                st.session_state.xp[user] = st.session_state.xp.get(user, 0) + 10
                                st.session_state.feed.insert(0, {
                                    "id": st.session_state.next_post_id,
                                    "user": user,
                                    "challenge": c["title"],
                                    "text": clean_text,
                                    "time": "gerade eben",
                                    "reactions": {},
                                    "comments": []
                                })
                                st.session_state.next_post_id += 1
                                st.session_state.checkin_message = "Gespeichert! Dein Fortschritt wurde aktualisiert. ✅"
                                st.rerun()
                            else:
                                st.warning("Bitte zuerst einen kurzen Check-in-Text eingeben.")
                else:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Beitreten", key=f"join_{c['id']}"):
                        c["members"].append(user)
                        st.rerun()

        # st.markdown("<hr>", unsafe_allow_html=True)


# ── TAB 2: FEED ────────────────────────────────────
with tab2:
    if not st.session_state.feed:
        st.write("Noch keine Posts. Mach einen Check-in!")
    for post in st.session_state.feed:
        if "id" not in post:
            post["id"] = st.session_state.next_post_id
            st.session_state.next_post_id += 1
        post.setdefault("reactions", {})
        post.setdefault("comments", [])

        with st.container(border=True):
            st.markdown(f"**{post['user']}** · *{post['challenge']}* · <span style='opacity:.65;font-size:.8rem'>{post['time']}</span>", unsafe_allow_html=True)
            st.write(post["text"])

            reaction_cols = st.columns(4)
            for emoji_index, emoji in enumerate(["🔥", "👏", "✅", "💪"]):
                count = post["reactions"].get(emoji, 0)
                if reaction_cols[emoji_index].button(f"{emoji} {count}", key=f"reaction_{post['id']}_{emoji}"):
                    post["reactions"][emoji] = count + 1
                    st.rerun()

            with st.expander("Kommentare"):
                if not post["comments"]:
                    st.caption("Noch keine Kommentare.")
                for comment in post["comments"]:
                    st.write(f"**{comment['user']}**: {comment['text']}")

                with st.form(f"comment_form_{post['id']}", clear_on_submit=True):
                    comment_text = st.text_input("Kommentar schreiben")
                    submitted_comment = st.form_submit_button("Kommentieren")

                if submitted_comment:
                    if comment_text.strip():
                        post["comments"].append({"user": user, "text": comment_text.strip()})
                        st.rerun()
                    else:
                        st.warning("Bitte zuerst einen Kommentar eingeben.")


# ── TAB 3: ERSTELLEN ───────────────────────────────
with tab3:
    st.markdown("**Neue Challenge**")

    if st.session_state.created_message:
        st.success(st.session_state.created_message)
        st.session_state.created_message = ""

    with st.form("create_challenge_form", clear_on_submit=True):
        title = st.text_input("Name der Challenge")
        desc  = st.text_area("Beschreibung (klare Regeln!)", height=80)
        goal  = st.text_input("Was ist das Ziel der Challenge?")
        cat   = st.selectbox("Kategorie", ["Fitness", "Bildung", "Ernährung", "Mindset"])
        days  = st.slider("Dauer in Tagen", 3, 90, 30)
        submitted = st.form_submit_button("Challenge erstellen 🚀")

    if submitted:
        if title.strip() and desc.strip() and goal.strip():
            new_id = max([c["id"] for c in st.session_state.challenges], default=0) + 1
            st.session_state.challenges.append({
                "id": new_id,
                "title": title.strip(),
                "desc": desc.strip(),
                "category": cat,
                "days": days,
                "goal": goal.strip(),
                "members": [user],
                "checkins": [],
                "progress": 0,
                "creator": user,
            })
            st.session_state.created_message = f"'{title.strip()}' wurde erstellt! Du bist automatisch dabei. ✅"
            st.rerun()
        else:
            st.warning("Titel, Beschreibung und Ziel ausfüllen!")


# ── TAB 4: MEINE FORTSCHRITTE ──────────────────────
with tab4:
    my_challenges = [c for c in st.session_state.challenges if user in c["members"]]

    if not my_challenges:
        st.markdown("<div class='empty-box'>Du bist noch keiner Challenge beigetreten.</div>", unsafe_allow_html=True)
    else:
        st.markdown("**Deine aktiven Challenges**")
        total_checkins = sum(len([checkin for checkin in c["checkins"] if checkin["user"] == user]) for c in my_challenges)
        badges = []
        if st.session_state.xp.get(user, 0) >= 10:
            badges.append("First Check-in")
        if st.session_state.xp.get(user, 0) >= 50:
            badges.append("XP Sammler")
        if total_checkins >= 5:
            badges.append("Streak Starter")

        if badges:
            st.markdown("**Deine Badges**")
            st.write(" · ".join([f"🏅 {badge}" for badge in badges]))
        else:
            st.caption("Noch keine Badges. Mach deinen ersten Check-in!")

        for c in my_challenges:
            with st.container(border=True):
                progress_days = min(c.get("progress", 0), c["days"])
                progress_percent = int((progress_days / max(c["days"], 1)) * 100)

                st.markdown(f"**{c['title']}**")
                st.caption(c["goal"])
                st.progress(progress_days / max(c["days"], 1))
                st.write(f"Tag {progress_days} von {c['days']} · {progress_percent}% geschafft")
                if progress_percent >= 100:
                    st.success("Badge: Challenge abgeschlossen 🏆")
                elif progress_percent >= 50:
                    st.info("Badge: Halbzeit erreicht 🏅")

                user_checkins = [checkin for checkin in c["checkins"] if checkin["user"] == user]
                st.caption(f"Deine Check-ins in dieser Challenge: {len(user_checkins)}")
                if user_checkins:
                    with st.expander("Meine bisherigen Check-ins anzeigen"):
                        for checkin in reversed(user_checkins):
                            st.write(f"{checkin['time']}: {checkin['text']}")


# ── TAB 5: LEADERBOARD ─────────────────────────────
with tab5:
    st.markdown("**Globales Leaderboard**")

    players = set(st.session_state.xp.keys())
    for challenge in st.session_state.challenges:
        players.update(challenge["members"])

    ranking = sorted(players, key=lambda player: st.session_state.xp.get(player, 0), reverse=True)

    if not ranking:
        st.markdown("<div class='empty-box'>Noch keine Punkte gesammelt.</div>", unsafe_allow_html=True)
    else:
        for index, player in enumerate(ranking, start=1):
            st.markdown(f"**#{index}** · {player} · {st.session_state.xp.get(player, 0)} XP")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**Leaderboard pro Challenge**")
    if not st.session_state.challenges:
        st.markdown("<div class='empty-box'>Keine Challenge verfügbar.</div>", unsafe_allow_html=True)
        st.stop()
    challenge_titles = [challenge["title"] for challenge in st.session_state.challenges]
    challenge_title = st.selectbox("Challenge auswählen", challenge_titles, key="leaderboard_challenge_select")
    selected_challenge = next((challenge for challenge in st.session_state.challenges if challenge["title"] == challenge_title), None)

    if selected_challenge is None:
        st.markdown("<div class='empty-box'>Keine Challenge verfügbar.</div>", unsafe_allow_html=True)
    else:
        challenge_ranking = []
        for member in selected_challenge["members"]:
            member_checkins = [checkin for checkin in selected_challenge["checkins"] if checkin["user"] == member]
            challenge_ranking.append((member, len(member_checkins)))

        challenge_ranking.sort(key=lambda item: item[1], reverse=True)

        for index, item in enumerate(challenge_ranking, start=1):
            member, checkin_count = item
            st.markdown(f"**#{index}** · {member} · {checkin_count} Check-ins")