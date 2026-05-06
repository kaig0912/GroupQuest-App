from datetime import date

from auth import authenticate_user, register_user
from db import init_db
from services import (
    create_challenge,
    create_checkin,
    delete_challenge,
    get_challenge,
    join_challenge,
    list_challenges,
    list_checkins,
    list_participants,
    update_challenge,
)


def test_user_challenge_and_checkin_flow(tmp_path):
    db_path = tmp_path / "groupquest.db"
    init_db(db_path)

    ok, _ = register_user("alice", "alice@example.com", "secret123", db_path)
    assert ok
    ok, _ = register_user("bob", "bob@example.com", "secret123", db_path)
    assert ok

    alice = authenticate_user("alice", "secret123", db_path)
    bob = authenticate_user("bob@example.com", "secret123", db_path)
    assert alice is not None
    assert bob is not None

    challenge_id = create_challenge(
        alice["id"],
        "7 Tage Lesen",
        "Jeden Tag 20 Minuten lesen.",
        7,
        "Taeglich ein kurzer Check-in.",
        True,
        date.today(),
        db_path,
    )

    challenges = list_challenges("lesen", db_path=db_path)
    assert len(challenges) == 1
    assert challenges[0]["participant_count"] == 1

    assert join_challenge(challenge_id, bob["id"], db_path)
    assert not join_challenge(challenge_id, bob["id"], db_path)
    assert len(list_participants(challenge_id, db_path)) == 2

    ok, message = create_checkin(challenge_id, bob["id"], "Tag 1 erledigt.", None, db_path)
    assert ok, message
    assert len(list_checkins(challenge_id=challenge_id, db_path=db_path)) == 1

    assert update_challenge(
        challenge_id,
        alice["id"],
        "7 Tage Lesen und Notizen",
        "Lesen plus Notizen.",
        7,
        "Check-in mit kurzer Notiz.",
        True,
        db_path,
    )
    assert get_challenge(challenge_id, db_path)["name"] == "7 Tage Lesen und Notizen"

    assert not delete_challenge(challenge_id, bob["id"], db_path)
    assert delete_challenge(challenge_id, alice["id"], db_path)
