from datetime import datetime
from flask import request, current_app, render_template, Blueprint, redirect, url_for, g
from scribe.server.db import get_db
from scribe.server.transcriber.worker import TranscriberWorker, ModelSize

from sqlite3 import Cursor

bp = Blueprint("scribe", __name__)
cache = {}


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "start_session" in request.form:
            start_session_form(request)
        elif "end_session" in request.form:
            end_session_form()
        return redirect(url_for("scribe.index"))

    db = get_db()
    past_sessions = get_past_sessions(db)
    current_sessions = get_active_sessions(db)
    if current_sessions and "transcriber" not in cache:
        create_worker(db, current_sessions)

    return render_template("session.html", past_sessions=past_sessions, current_sessions=current_sessions)


@bp.route("/upload", methods=["GET", "PUT"])
def upload_audio_file():
    if request.method in ["PUT"]:
        file = request.files["file"]
        date_string = datetime.now().isoformat()
        file.save(f"/tmp/scribe/uploads/audio/{date_string}")
        if cache.get("transcriber"):
            cache["transcriber"].transcribe(f"/tmp/scribe/uploads/audio/{date_string}")
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
        SELECT 
            * 
        FROM sessions s
        LEFT JOIN transcriptions t
            ON t.session_id = s.session_id
        WHERE s.end_ts IS NOT NULL
        ORDER BY end_ts DESC
        LIMIT 5
        """
    ).fetchall()
    return past_sessions


def start_session_form(request):
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

        active_session = get_active_sessions(db)
        session_id = active_session[0]["session_id"]
        storage_backend = "LOCAL_FILESYSTEM"
        location = f"/tmp/scribe/transcriptions/{session_id}_{session_name}"

        db.execute(
            """
            INSERT INTO transcriptions (session_id, storage_backend, location)
            VALUES(?, ?, ?)
            """,
            (session_id, storage_backend, location)
        )
        db.commit()
        cache["transcriber"] = TranscriberWorker(ModelSize.MEDIUM, location, location)


def create_worker(db, current_sessions):
    transcription = db.execute(
        "SELECT * FROM transcriptions WHERE session_id = ?",
        str(current_sessions[0]["session_id"])) \
        .fetchall()
    cache["transcriber"] = TranscriberWorker(ModelSize.MEDIUM,
                                             transcription[0]["location"],
                                             transcription[0]["location"])


def end_worker(e=None):
    transcriber: TranscriberWorker = cache.pop("transcriber", None)

    if transcriber is not None:
        transcriber.end_session()


def end_session_form():
    db = get_db()
    active_session = get_active_sessions(db)[0]
    db.execute(
        f"""
        UPDATE sessions SET end_ts=datetime()
        WHERE session_id = ?
        """,
        (f"{active_session['session_id']}")
    )
    db.commit()
    end_worker()


@bp.route("/healthcheck")
def healthcheck():
    return "200 OK"
