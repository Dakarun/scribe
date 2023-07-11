from flask import Flask
import scribe.server.webserver


def create_app():
    app = Flask("webserver", template_folder="scribe/resources/templates/", static_folder="scribe/resources/static/")
    # existing code omitted

    from scribe.server import db
    db.init_app(app)
    app.register_blueprint(webserver.bp)
    return app
