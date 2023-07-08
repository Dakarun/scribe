from flask import Flask


def create_app():
    app = Flask("webserver")
    # existing code omitted

    from scribe.server import db
    db.init_app(app)

    return app