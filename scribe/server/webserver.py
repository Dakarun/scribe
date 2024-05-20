from datetime import datetime
from flask import request, render_template, Blueprint, redirect, url_for
from scribe.server.db import db_session
# from scribe.server.exceptions import NoActiveSession
from scribe.server.transcriber.worker import TranscriberWorker, ModelSize
from scribe.server.models import Session, SessionEntry, Transcription, TranscriptionEntry
from pathlib import Path

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

    past_sessions = get_past_sessions()
    current_sessions = get_active_sessions()
    if current_sessions and "transcriber" not in cache:
        create_worker(current_sessions)

    return render_template("session.html", past_sessions=past_sessions, current_sessions=current_sessions)


@bp.route("/upload", methods=["GET", "PUT"])
def upload_audio_file():
    Path("/tmp/scribe/uploads/audio/").mkdir(parents=True, exist_ok=True)  # TODO: Move into central bootstrapping
    if not get_active_sessions():
        response = {"exception": "No active sessions found"}
        return response, 400
    if request.method in ["PUT"]:
        file = request.files["file"]
        date_string = datetime.now().isoformat()
        file.save(f"/tmp/scribe/uploads/audio/{date_string}")
        if not cache.get("transcriber"):
            current_sessions = get_active_sessions()
            if len(current_sessions):
                create_worker(current_sessions)
            else:
                # TODO: Fix cyclical imports
                # raise NoActiveSession()
                pass
        cache["transcriber"].transcribe(f"/tmp/scribe/uploads/audio/{date_string}")
        response = {"filename": f"/tmp/scribe/uploads/audio/{date_string}"}
        return response, 200
    elif request.method == "GET":
        return "<p>Upload endpoint</p>"


def get_active_sessions():
    active_sessions = Session.query.filter(Session.end_ts == None).order_by(Session.session_id.desc()).all()
    return active_sessions


def get_past_sessions():
    past_sessions = Session.query \
        .join(Transcription, Session.session_id == Transcription.transcription_id) \
        .filter(Session.end_ts != None)
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
        now = datetime.now()
        session = Session(name=session_name, description=session_description, created_ts=now)
        db_session.add(session)
        db_session.commit()

        active_session = get_active_sessions()
        session_id = active_session[0].session_id
        storage_backend = "LOCAL_FILESYSTEM"
        location = f"{session_id}_{session_name}"

        now = datetime.now()
        transcription = Transcription(session_id=session_id, storage_backend=storage_backend, base_location=location,
                                      created_ts=now, updated_ts=now, default_transcription=True)
        db_session.add(transcription)
        db_session.commit()
        cache["transcriber"] = TranscriberWorker(ModelSize.MEDIUM, location, location)


def create_worker(current_sessions):
    print("Creating worker")
    session_id = str(current_sessions[0].session_id)
    transcription = Transcription.query.filter(Transcription.session_id == session_id).all()
    cache["transcriber"] = TranscriberWorker(ModelSize.BASE_EN, transcription[0].base_location,
                                             transcription[0].base_location)
    print("Worker created")


def end_worker(e=None):
    transcriber: TranscriberWorker = cache.pop("transcriber", None)

    if transcriber is not None:
        transcriber.end_session()


def end_session_form():
    active_session = get_active_sessions()[0]
    active_session.end_ts = datetime.now()
    db_session.commit()
    end_worker()


@bp.route("/healthcheck")
def healthcheck():
    return "200 OK"
