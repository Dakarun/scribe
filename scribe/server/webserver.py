from datetime import datetime
from flask import request, current_app, render_template, Blueprint, redirect, url_for
from scribe.server.db import get_db

from sqlite3 import Cursor

bp = Blueprint("scribe", __name__)


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session_name = request.form["name"]
        session_description = request.form["description"]
        error = None

        if not session_name:
            error = "Session must have a name"

        if error:
            raise Exception(error)
        else:
            db = get_db()
            db.execute(
                f"""
                INSERT INTO sessions (name, description, start_ts)
                VALUES(?, ?, datetime())
                """,
                (session_name, session_description)
            )
            db.commit()
            return redirect(url_for("scribe.index"))

    db = get_db()
    past_sessions = get_past_sessions(db)
    current_sessions = get_active_sessions(db)

    return render_template("session.html", past_sessions=past_sessions, current_sessions=current_sessions)


@bp.route("/upload", methods=["GET", "PUT"])
def upload_audio_file():
    if request.method in ["PUT"]:
        file = request.files["file"]
        date_string = datetime.now().isoformat()
        file.save(f"/tmp/scribe/uploads/audio/{date_string}")
        return {"ResponseCode": "200", "FileName": f"/tmp/scribe/uploads/audio/{date_string}"}
    elif request.method == "GET":
        return "<p>Upload endpoint</p>"


def get_active_sessions(db: Cursor):
    active_sessions = db.execute(
        """
        SELECT * FROM sessions WHERE end_ts IS NULL
        """
    ).fetchall()
    return active_sessions


def get_past_sessions(db: Cursor):
    past_sessions = db.execute(
        """
        SELECT * FROM sessions WHERE end_ts IS NULL
        """
    ).fetchall()
    return past_sessions


@bp.route("/healthcheck")
def healthcheck():
    return "200 OK"
