"""Minimal local identity/session manager for a single-tenant deployment host.

Passwords use stdlib scrypt. Sessions are random opaque bearer tokens; only token
hashes are persisted. Put the API behind HTTPS and a rate-limiting reverse proxy.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from .storage import AuditStore, Database, utc_now


@dataclass(frozen=True, slots=True)
class UserIdentity:
    id: str
    username: str
    role: str


@dataclass(frozen=True, slots=True)
class Session:
    access_token: str
    token_type: str
    expires_at: str
    user: UserIdentity


def _password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return f"scrypt${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt_text, digest_text = encoded.split("$", 2)
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=len(expected))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


class AuthManager:
    def __init__(self, database: Database, *, session_hours: int = 12, audit: AuditStore | None = None) -> None:
        if not 1 <= session_hours <= 168:
            raise ValueError("session_hours must be between 1 and 168")
        self.database = database
        self.session_hours = session_hours
        self.audit = audit or AuditStore(database)

    def register(self, username: str, password: str) -> UserIdentity:
        username = username.strip().lower() if isinstance(username, str) else ""
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{2,31}", username):
            raise ValueError("username must be 3-32 characters: letters, digits, dot, dash, underscore")
        if not isinstance(password, str) or not 12 <= len(password) <= 1024:
            raise ValueError("password must contain between 12 and 1024 characters")
        user_id = str(uuid.uuid4())
        encoded = _password_hash(password)
        with self.database.connect() as conn:
            try:
                conn.execute(
                    "INSERT INTO users(id,username,password_hash,role,created_at) VALUES(?,?,?,?,?)",
                    (user_id, username, encoded, "trader", utc_now()),
                )
                self.audit.record_in_connection(
                    conn, user_id=user_id, action="auth.register",
                    entity_type="user", entity_id=user_id,
                )
            except Exception as exc:
                if "UNIQUE constraint failed" in str(exc):
                    raise ValueError("username is already registered") from exc
                raise
        return UserIdentity(user_id, username, "trader")

    def login(self, username: str, password: str) -> Session:
        with self.database.connect() as conn:
            row = conn.execute(
                "SELECT id,username,password_hash,role FROM users WHERE username=? COLLATE NOCASE",
                (username.strip(),),
            ).fetchone()
        if row is None or not _verify_password(password, row["password_hash"]):
            raise ValueError("invalid username or password")
        token = secrets.token_urlsafe(40)
        expires = datetime.now(UTC) + timedelta(hours=self.session_hours)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self.database.connect() as conn:
            conn.execute(
                "INSERT INTO sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
                (token_hash, row["id"], utc_now(), expires.isoformat()),
            )
            self.audit.record_in_connection(
                conn, user_id=row["id"], action="auth.login",
                entity_type="session", entity_id=token_hash[:16],
            )
        identity = UserIdentity(row["id"], row["username"], row["role"])
        return Session(token, "Bearer", expires.isoformat(), identity)

    def resolve(self, token: str) -> UserIdentity | None:
        if not isinstance(token, str) or not 20 <= len(token) <= 200:
            return None
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self.database.connect() as conn:
            row = conn.execute(
                "SELECT u.id,u.username,u.role,s.expires_at,s.revoked_at FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=?",
                (token_hash,),
            ).fetchone()
        if row is None or row["revoked_at"] is not None:
            return None
        try:
            expires = datetime.fromisoformat(row["expires_at"])
        except ValueError:
            return None
        if expires <= datetime.now(UTC):
            return None
        return UserIdentity(row["id"], row["username"], row["role"])

    def logout(self, token: str) -> bool:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self.database.connect() as conn:
            row = conn.execute("SELECT user_id FROM sessions WHERE token_hash=? AND revoked_at IS NULL", (token_hash,)).fetchone()
            if row is None:
                return False
            conn.execute("UPDATE sessions SET revoked_at=? WHERE token_hash=?", (utc_now(), token_hash))
            self.audit.record_in_connection(
                conn, user_id=row["user_id"], action="auth.logout",
                entity_type="session", entity_id=token_hash[:16],
            )
        return True
