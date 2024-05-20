import click

from flask import Flask
from scribe.server.db import db_session, init_db
import scribe.server.webserver


app = Flask("webserver", template_folder="scribe/resources/templates/", static_folder="scribe/resources/static/")
app.register_blueprint(webserver.bp)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.cli.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database")
