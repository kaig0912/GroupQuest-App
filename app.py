from __future__ import annotations

from datetime import date

import streamlit as st

from auth import authenticate_user, get_user, register_user
from db import init_db
from services import (
    create_challenge,
    create_checkin,
    delete_challenge,
    get_challenge,
    is_participant,
    join_challenge,
    list_challenges,
    list_checkins,
    list_participants,
    save_uploaded_file,
    update_challenge,
    update_profile,
    validate_checkin,
)


st.set_page_config(page_title="GroupQuest", page_icon=":dart:", layout="wide")
init_db()


def current_user() -> dict | None:
    user_id = st.session_state.get("user_id")
    return get_user(user_id) if user_id else None


def require_login() -> dict | None:
    user = current_user()
    if user is None:
        st.info("Bitte logge dich ein oder registriere dich, um GroupQuest zu nutzen.")
    return user


def login_register_view() -> None:
    st.title("GroupQuest")
    st.caption("Gemeinsam Challenges starten, Fortschritt dokumentieren und dranbleiben.")

    login_tab, register_tab = st.tabs(["Login", "Registrieren"])
    with login_tab:
        with st.form("login_form"):
            identifier = st.text_input("Benutzername oder E-Mail")
            password = st.text_input("Passwort", type="password")
            submitted = st.form_submit_button("Einloggen")
        if submitted:
            user = authenticate_user(identifier, password)
            if user:
                st.session_state["user_id"] = user["id"]
                st.success("Du bist eingeloggt.")
                st.rerun()
            else:
                st.error("Login fehlgeschlagen. Bitte pruefe deine Daten.")

    with register_tab:
        with st.form("register_form"):
            username = st.text_input("Benutzername")
            email = st.text_input("E-Mail")
            password = st.text_input("Passwort", type="password")
            submitted = st.form_submit_button("Account erstellen")
        if submitted:
            ok, message = register_user(username, email, password)
            if ok:
                st.success(message)
            else:
                st.error(message)


def profile_view(user: dict) -> None:
    st.header("Profil")
    with st.form("profile_form"):
        display_name = st.text_input("Anzeigename", value=user["display_name"])
        bio = st.text_area("Bio", value=user["bio"], height=120)
        photo = st.file_uploader("Profilfoto", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Profil speichern")

    if submitted:
        photo_path = save_uploaded_file(photo, f"profile_{user['id']}") if photo else None
        update_profile(user["id"], display_name, bio, photo_path)
        st.success("Profil wurde aktualisiert.")
        st.rerun()

    st.subheader("Meine Check-ins")
    render_checkins(list_checkins(user_id=user["id"]))


def challenge_overview(user: dict) -> None:
    st.header("Challenges")
    col_search, col_public = st.columns([3, 1])
    search = col_search.text_input("Suchen/filtern", placeholder="Name, Beschreibung oder Regeln")
    public_only = col_public.toggle("Nur oeffentliche", value=True)

    challenges = list_challenges(search=search, public_only=public_only)
    if not challenges:
        st.info("Noch keine passenden Challenges gefunden.")
        return

    for challenge in challenges:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            left.subheader(challenge["name"])
            left.write(challenge["description"])
            left.caption(
                f"Creator: {challenge['creator_name']} | "
                f"{challenge['duration_days']} Tage | "
                f"{challenge['participant_count']} Teilnehmende | "
                f"{challenge['checkin_count']} Check-ins"
            )
            if right.button("Oeffnen", key=f"open_{challenge['id']}"):
                st.session_state["selected_challenge_id"] = challenge["id"]
                st.rerun()


def create_challenge_view(user: dict) -> None:
    st.header("Challenge erstellen")
    with st.form("create_challenge_form"):
        name = st.text_input("Name")
        description = st.text_area("Beschreibung", height=100)
        duration_days = st.number_input("Dauer in Tagen", min_value=1, max_value=365, value=7)
        rules = st.text_area("Regeln", height=120)
        start = st.date_input("Startdatum", value=date.today())
        is_public = st.checkbox("Oeffentlich sichtbar", value=True)
        submitted = st.form_submit_button("Challenge erstellen")

    if submitted:
        if not name.strip() or not description.strip() or not rules.strip():
            st.error("Name, Beschreibung und Regeln sind Pflichtfelder.")
            return
        challenge_id = create_challenge(user["id"], name, description, duration_days, rules, is_public, start)
        st.session_state["selected_challenge_id"] = challenge_id
        st.success("Challenge wurde erstellt.")
        st.rerun()


def challenge_detail(user: dict, challenge_id: int) -> None:
    challenge = get_challenge(challenge_id)
    if challenge is None:
        st.error("Diese Challenge existiert nicht mehr.")
        st.session_state.pop("selected_challenge_id", None)
        return

    if st.button("Zurueck zur Uebersicht"):
        st.session_state.pop("selected_challenge_id", None)
        st.rerun()

    st.header(challenge["name"])
    st.write(challenge["description"])
    st.caption(f"Creator: {challenge['creator_name']} | Start: {challenge['start_date']} | Dauer: {challenge['duration_days']} Tage")
    st.markdown("**Regeln**")
    st.write(challenge["rules"])

    participant = is_participant(challenge_id, user["id"])
    if participant:
        st.success("Du nimmst an dieser Challenge teil.")
    elif st.button("Challenge beitreten"):
        if join_challenge(challenge_id, user["id"]):
            st.success("Du bist der Challenge beigetreten.")
            st.rerun()
        else:
            st.info("Du bist bereits Teil dieser Challenge.")

    tab_checkins, tab_people, tab_manage = st.tabs(["Check-ins", "Teilnehmende", "Bearbeiten"])
    with tab_checkins:
        if participant:
            with st.form(f"checkin_form_{challenge_id}"):
                text = st.text_area("Taeglicher Check-in", placeholder="Was hast du heute geschafft?", height=100)
                photo = st.file_uploader("Foto hochladen", type=["png", "jpg", "jpeg"])
                submitted = st.form_submit_button("Check-in speichern")
            if submitted:
                photo_path = save_uploaded_file(photo, f"checkin_{challenge_id}_{user['id']}") if photo else None
                ok, message = create_checkin(challenge_id, user["id"], text, photo_path)
                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("Tritt der Challenge bei, um Check-ins einzureichen.")
        render_checkins(list_checkins(challenge_id=challenge_id), allow_validate=True, user_id=user["id"])

    with tab_people:
        participants = list_participants(challenge_id)
        for person in participants:
            st.write(f"**{person['display_name']}** (@{person['username']})")
            if person["bio"]:
                st.caption(person["bio"])

    with tab_manage:
        if challenge["creator_id"] != user["id"]:
            st.info("Nur der Creator kann diese Challenge bearbeiten.")
            return

        with st.form(f"edit_challenge_{challenge_id}"):
            name = st.text_input("Name", value=challenge["name"])
            description = st.text_area("Beschreibung", value=challenge["description"], height=100)
            duration_days = st.number_input("Dauer in Tagen", min_value=1, max_value=365, value=int(challenge["duration_days"]))
            rules = st.text_area("Regeln", value=challenge["rules"], height=120)
            is_public = st.checkbox("Oeffentlich sichtbar", value=bool(challenge["is_public"]))
            saved = st.form_submit_button("Aenderungen speichern")
        if saved:
            update_challenge(challenge_id, user["id"], name, description, duration_days, rules, is_public)
            st.success("Challenge wurde aktualisiert.")
            st.rerun()

        st.divider()
        if st.button("Challenge loeschen", type="primary"):
            delete_challenge(challenge_id, user["id"])
            st.session_state.pop("selected_challenge_id", None)
            st.success("Challenge wurde geloescht.")
            st.rerun()


def render_checkins(checkins: list[dict], allow_validate: bool = False, user_id: int | None = None) -> None:
    if not checkins:
        st.info("Noch keine Check-ins vorhanden.")
        return

    for checkin in checkins:
        with st.container(border=True):
            st.write(f"**{checkin['display_name']}** in **{checkin['challenge_name']}**")
            st.caption(checkin["created_at"])
            if checkin["text"]:
                st.write(checkin["text"])
            if checkin["photo_path"]:
                st.image(checkin["photo_path"], width=260)
            st.caption(f"{checkin['validation_count']} Bestaetigungen")
            if allow_validate and user_id and checkin["user_id"] != user_id:
                if st.button("Check-in bestaetigen", key=f"validate_{checkin['id']}"):
                    if validate_checkin(checkin["id"], user_id):
                        st.success("Check-in bestaetigt.")
                        st.rerun()
                    else:
                        st.info("Du hast diesen Check-in bereits bestaetigt.")


def main() -> None:
    user = current_user()

    with st.sidebar:
        st.title("GroupQuest")
        if user:
            st.write(f"Angemeldet als **{user['display_name']}**")
            page = st.radio("Navigation", ["Challenges", "Neue Challenge", "Profil"])
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()
        else:
            page = "Login"

    if not user:
        login_register_view()
        return

    selected_challenge_id = st.session_state.get("selected_challenge_id")
    if selected_challenge_id and page == "Challenges":
        challenge_detail(user, int(selected_challenge_id))
    elif page == "Challenges":
        challenge_overview(user)
    elif page == "Neue Challenge":
        create_challenge_view(user)
    elif page == "Profil":
        profile_view(user)


if __name__ == "__main__":
    main()
