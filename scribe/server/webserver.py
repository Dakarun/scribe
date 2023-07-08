from datetime import datetime
from flask import request, current_app


@current_app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@current_app.route("/upload", methods=["GET", "PUT"])
def upload_audio_file():
    if request.method in ["PUT"]:
        file = request.files["file"]
        date_string = datetime.now().isoformat()
        file.save(f"/tmp/scribe/uploads/audio/{date_string}")
        return {"ResponseCode": "200", "FileName": f"/tmp/scribe/uploads/audio/{date_string}"}
    elif request.method == "GET":
        return "<p>Upload endpoint</p>"
