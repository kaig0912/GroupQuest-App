from __future__ import annotations

from datetime import date
from pathlib import Path
from sqlite3 import IntegrityError

from db import UPLOAD_DIR, get_connection


def save_uploaded_file(uploaded_file, prefix: str) -> str | None:
    if uploaded_file is None:
        return None

    UPLOAD_DIR.mkdir(exist_ok=True)
    safe_name = Path(uploaded_file.name).name.replace(" ", "_")
    target = UPLOAD_DIR / f"{prefix}_{safe_name}"
    target.write_bytes(uploaded_file.getbuffer())
    return str(target)


def update_profile(user_id: int, display_name: str, bio: str, photo_path: str | None = None, db_path=None) -> None:
    with get_connection(db_path) as conn:
        if photo_path:
            conn.execute(
                "UPDATE users SET display_name = ?, bio = ?, photo_path = ? WHERE id = ?",
                (display_name.strip(), bio.strip(), photo_path, user_id),
            )
        else:
            conn.execute(
                "UPDATE users SET display_name = ?, bio = ? WHERE id = ?",
                (display_name.strip(), bio.strip(), user_id),
            )


def create_challenge(
    creator_id: int,
    name: str,
    description: str,
    duration_days: int,
    rules: str,
    is_public: bool,
    start_date: date,
    db_path=None,
) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO challenges
                (creator_id, name, description, duration_days, rules, is_public, start_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                creator_id,
                name.strip(),
                description.strip(),
                int(duration_days),
                rules.strip(),
                int(is_public),
                start_date.isoformat(),
            ),
        )
        challenge_id = int(cursor.lastrowid)
        conn.execute(
            "INSERT OR IGNORE INTO challenge_participants (user_id, challenge_id) VALUES (?, ?)",
            (creator_id, challenge_id),
        )
    return challenge_id


def list_challenges(search: str = "", public_only: bool = True, db_path=None) -> list[dict]:
    query = """
        SELECT c.*, u.display_name AS creator_name,
               COUNT(DISTINCT p.user_id) AS participant_count,
               COUNT(DISTINCT ci.id) AS checkin_count
        FROM challenges c
        JOIN users u ON u.id = c.creator_id
        LEFT JOIN challenge_participants p ON p.challenge_id = c.id
        LEFT JOIN checkins ci ON ci.challenge_id = c.id
        WHERE (? = 0 OR c.is_public = 1)
          AND (
              ? = ''
              OR lower(c.name) LIKE ?
              OR lower(c.description) LIKE ?
              OR lower(c.rules) LIKE ?
          )
        GROUP BY c.id
        ORDER BY c.created_at DESC
    """
    term = search.strip().lower()
    pattern = f"%{term}%"
    with get_connection(db_path) as conn:
        rows = conn.execute(query, (int(public_only), term, pattern, pattern, pattern)).fetchall()
    return [dict(row) for row in rows]


def get_challenge(challenge_id: int, db_path=None) -> dict | None:
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT c.*, u.display_name AS creator_name
            FROM challenges c
            JOIN users u ON u.id = c.creator_id
            WHERE c.id = ?
            """,
            (challenge_id,),
        ).fetchone()
    return dict(row) if row else None


def update_challenge(challenge_id: int, user_id: int, name: str, description: str, duration_days: int, rules: str, is_public: bool, db_path=None) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE challenges
            SET name = ?, description = ?, duration_days = ?, rules = ?, is_public = ?
            WHERE id = ? AND creator_id = ?
            """,
            (name.strip(), description.strip(), int(duration_days), rules.strip(), int(is_public), challenge_id, user_id),
        )
    return cursor.rowcount == 1


def delete_challenge(challenge_id: int, user_id: int, db_path=None) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM challenges WHERE id = ? AND creator_id = ?",
            (challenge_id, user_id),
        )
    return cursor.rowcount == 1


def join_challenge(challenge_id: int, user_id: int, db_path=None) -> bool:
    try:
        with get_connection(db_path) as conn:
            conn.execute(
                "INSERT INTO challenge_participants (user_id, challenge_id) VALUES (?, ?)",
                (user_id, challenge_id),
            )
    except IntegrityError:
        return False
    return True


def is_participant(challenge_id: int, user_id: int, db_path=None) -> bool:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM challenge_participants WHERE challenge_id = ? AND user_id = ?",
            (challenge_id, user_id),
        ).fetchone()
    return row is not None


def list_participants(challenge_id: int, db_path=None) -> list[dict]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT u.id, u.display_name, u.username, u.bio, p.joined_at
            FROM challenge_participants p
            JOIN users u ON u.id = p.user_id
            WHERE p.challenge_id = ?
            ORDER BY p.joined_at ASC
            """,
            (challenge_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_checkin(challenge_id: int, user_id: int, text: str, photo_path: str | None = None, db_path=None) -> tuple[bool, str]:
    if not text.strip() and not photo_path:
        return False, "Bitte schreibe einen kurzen Check-in oder lade ein Foto hoch."
    if not is_participant(challenge_id, user_id, db_path):
        return False, "Du musst der Challenge beitreten, bevor du einchecken kannst."

    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO checkins (challenge_id, user_id, text, photo_path) VALUES (?, ?, ?, ?)",
            (challenge_id, user_id, text.strip(), photo_path),
        )
    return True, "Check-in gespeichert."


def list_checkins(challenge_id: int | None = None, user_id: int | None = None, db_path=None) -> list[dict]:
    filters = []
    params = []
    if challenge_id is not None:
        filters.append("ci.challenge_id = ?")
        params.append(challenge_id)
    if user_id is not None:
        filters.append("ci.user_id = ?")
        params.append(user_id)
    where = f"WHERE {' AND '.join(filters)}" if filters else ""

    with get_connection(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT ci.*, u.display_name, c.name AS challenge_name,
                   COUNT(v.user_id) AS validation_count
            FROM checkins ci
            JOIN users u ON u.id = ci.user_id
            JOIN challenges c ON c.id = ci.challenge_id
            LEFT JOIN checkin_validations v ON v.checkin_id = ci.id
            {where}
            GROUP BY ci.id
            ORDER BY ci.created_at DESC
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def validate_checkin(checkin_id: int, user_id: int, db_path=None) -> bool:
    try:
        with get_connection(db_path) as conn:
            conn.execute(
                "INSERT INTO checkin_validations (checkin_id, user_id) VALUES (?, ?)",
                (checkin_id, user_id),
            )
    except IntegrityError:
        return False
    return True
