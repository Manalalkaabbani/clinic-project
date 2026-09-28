import os
import re
import secrets
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()
user_management = Blueprint("user_management", __name__)

MANAGED_ROLES = {"admin", "staff", "viewer"}
PASSWORD_MIN_LENGTH = 12
USERNAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,49}$")


class UserAccount(db.Model):
    __tablename__ = "platform_users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    display_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="staff")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    def to_public_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def load_secret_key():
    configured_key = os.environ.get("SECRET_KEY")
    if configured_key:
        return configured_key

    key_path = os.path.join(os.path.dirname(__file__), ".secret_key")
    try:
        with open(key_path, "r", encoding="utf-8") as key_file:
            return key_file.read().strip()
    except FileNotFoundError:
        secret_key = secrets.token_urlsafe(48)
        try:
            with open(key_path, "x", encoding="utf-8") as key_file:
                key_file.write(secret_key)
        except FileExistsError:
            with open(key_path, "r", encoding="utf-8") as key_file:
                return key_file.read().strip()
        return secret_key


def _session_user(user):
    session.clear()
    session["user_id"] = user.user_id
    session.permanent = True


def _validate_username(username):
    return isinstance(username, str) and USERNAME_PATTERN.fullmatch(username) is not None


def _validate_password(password):
    return isinstance(password, str) and len(password) >= PASSWORD_MIN_LENGTH


def _owner_error():
    current_user = getattr(g, "current_user", None)
    if current_user is None:
        return jsonify({"error": "Sign in is required."}), 401
    if current_user.role != "super_admin":
        return jsonify({"error": "Only the platform owner can manage users."}), 403
    return None


@user_management.get("/session")
def session_info():
    current_user = getattr(g, "current_user", None)
    return jsonify({
        "setup_required": UserAccount.query.first() is None,
        "user": current_user.to_public_dict() if current_user else None,
    })


@user_management.post("/setup")
def setup_owner():
    if UserAccount.query.first() is not None:
        return jsonify({"error": "The platform owner account has already been created."}), 409

    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    display_name = data.get("display_name", "").strip()
    password = data.get("password", "")

    if not _validate_username(username):
        return jsonify({"error": "Use 3-50 lowercase letters, numbers, dots, dashes, or underscores for the username."}), 400
    if not display_name or len(display_name) > 100:
        return jsonify({"error": "Enter a name no longer than 100 characters."}), 400
    if not _validate_password(password):
        return jsonify({"error": f"Password must be at least {PASSWORD_MIN_LENGTH} characters."}), 400

    owner = UserAccount(
        username=username,
        display_name=display_name,
        password_hash=generate_password_hash(password),
        role="super_admin",
        is_active=True,
    )
    db.session.add(owner)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not create the owner account. Check that the username is available."}), 409

    _session_user(owner)
    return jsonify({"user": owner.to_public_dict()}), 201


@user_management.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    user = UserAccount.query.filter_by(username=username.strip().lower()).first() if isinstance(username, str) else None

    if user is None or not user.is_active or not isinstance(password, str) or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Username or password is incorrect."}), 401

    _session_user(user)
    return jsonify({"user": user.to_public_dict()})


@user_management.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Signed out."})


@user_management.get("/users")
def list_users():
    error = _owner_error()
    if error:
        return error
    users = UserAccount.query.order_by(UserAccount.created_at.desc(), UserAccount.username).all()
    return jsonify([user.to_public_dict() for user in users])


@user_management.post("/users")
def create_user():
    error = _owner_error()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    display_name = data.get("display_name", "").strip()
    password = data.get("password", "")
    role = data.get("role", "staff")

    if not _validate_username(username):
        return jsonify({"error": "Use 3-50 lowercase letters, numbers, dots, dashes, or underscores for the username."}), 400
    if not display_name or len(display_name) > 100:
        return jsonify({"error": "Enter a name no longer than 100 characters."}), 400
    if not _validate_password(password):
        return jsonify({"error": f"Password must be at least {PASSWORD_MIN_LENGTH} characters."}), 400
    if role not in MANAGED_ROLES:
        return jsonify({"error": "Choose Admin, Staff, or Viewer for this account."}), 400

    user = UserAccount(
        username=username,
        display_name=display_name,
        password_hash=generate_password_hash(password),
        role=role,
        is_active=True,
    )
    db.session.add(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not create this account. The username may already exist."}), 409
    return jsonify(user.to_public_dict()), 201


@user_management.patch("/users/<int:user_id>")
def update_user(user_id):
    error = _owner_error()
    if error:
        return error

    user = db.session.get(UserAccount, user_id)
    if user is None:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json(silent=True) or {}
    if user.role == "super_admin":
        if data.get("role", "super_admin") != "super_admin" or data.get("is_active") is False:
            return jsonify({"error": "The platform owner account cannot be demoted or deactivated."}), 400
    elif "role" in data and data["role"] not in MANAGED_ROLES:
        return jsonify({"error": "Choose Admin, Staff, or Viewer for this account."}), 400

    if "display_name" in data:
        display_name = data["display_name"].strip() if isinstance(data["display_name"], str) else ""
        if not display_name or len(display_name) > 100:
            return jsonify({"error": "Enter a name no longer than 100 characters."}), 400
        user.display_name = display_name

    if "role" in data and user.role != "super_admin":
        user.role = data["role"]

    if "is_active" in data:
        if not isinstance(data["is_active"], bool):
            return jsonify({"error": "Account status must be active or inactive."}), 400
        if user.user_id == g.current_user.user_id and not data["is_active"]:
            return jsonify({"error": "You cannot deactivate your own account."}), 400
        user.is_active = data["is_active"]

    if data.get("password"):
        if not _validate_password(data["password"]):
            return jsonify({"error": f"Password must be at least {PASSWORD_MIN_LENGTH} characters."}), 400
        user.password_hash = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify(user.to_public_dict())


def register_user_management(app):
    app.register_blueprint(user_management, url_prefix="/api/auth")

    @app.before_request
    def protect_api():
        if not request.path.startswith("/api/") or request.method == "OPTIONS":
            return None

        public_endpoints = {
            "user_management.session_info",
            "user_management.setup_owner",
            "user_management.login",
        }
        if request.endpoint in public_endpoints:
            user_id = session.get("user_id")
            if user_id:
                user = db.session.get(UserAccount, user_id)
                if user is not None and user.is_active:
                    g.current_user = user
                else:
                    session.clear()
            return None

        user_id = session.get("user_id")
        user = db.session.get(UserAccount, user_id) if user_id else None
        if user is None or not user.is_active:
            session.clear()
            return jsonify({"error": "Sign in to continue."}), 401

        g.current_user = user
        if user.role == "viewer" and request.method not in {"GET", "HEAD"}:
            return jsonify({"error": "Viewer accounts have read-only access."}), 403
        if user.role == "staff" and request.method in {"PUT", "PATCH", "DELETE"}:
            return jsonify({"error": "Staff accounts cannot edit or delete records."}), 403
        if request.path == "/api/import/csv" and user.role not in {"admin", "super_admin"}:
            return jsonify({"error": "Only administrators can import data."}), 403
        return None


def initialize_user_table(app):
    with app.app_context():
        UserAccount.__table__.create(db.engine, checkfirst=True)