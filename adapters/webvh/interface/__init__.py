from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from flask_avatars import Avatars
from .storage import AskarStorage
from locust.env import Environment
from locust.log import setup_logging
from locust.html import get_html_report
from wtforms import (
    IntegerRangeField,
    SubmitField,
    SelectField,
)
from wtforms.validators import InputRequired
import asyncio
import uuid
import hashlib
from locustfiles import LOCUST_FILES
from settings import Settings
import gevent

setup_logging("INFO")


def create_app():
    app = Flask(__name__)
    app.secret_key = hashlib.sha1(Settings.WITNESS_SEED.encode()).hexdigest()

    Avatars(app)

    class LocustConfigForm(FlaskForm):
        feature = SelectField("Feature", [InputRequired()])
        swarm_size = IntegerRangeField("Swarm Size", [InputRequired()], default=1)
        duration = IntegerRangeField("Duration", [InputRequired()], default=20)
        submit = SubmitField("Run")

    @app.before_request
    def before_request_callback():
        session["swarm_max"] = 10
        session["spawn_rate"] = 1
        session["minutes_max"] = 5
        if "client_id" not in session:
            session["client_id"] = hashlib.sha1(str(uuid.uuid4()).encode()).hexdigest()
            asyncio.run(
                AskarStorage().store(
                    "report",
                    session["client_id"],
                    {
                        "message": "Run your first test and your report will appear here!"
                    },
                )
            )

    @app.route("/", methods=["GET", "POST"])
    def index():
        form = LocustConfigForm()
        form.feature.choices = [(file_name, file_name) for file_name in LOCUST_FILES]
        if request.method == "POST":
            # Get form data
            # TODO, enable multiple feature files
            features = [form.feature.data]
            duration = form.duration.data
            swarm_size = form.swarm_size.data

            # https://docs.locust.io/en/stable/use-as-lib.html
            # Load locust environment
            user_classes = [LOCUST_FILES[feature] for feature in features]
            env = Environment(user_classes=user_classes)

            # Create runner
            runner = env.create_local_runner()
            env.events.init.fire(environment=env, runner=runner)

            # TODO, implement distributed testing
            # Start load testing
            runner.start(swarm_size, spawn_rate=session["spawn_rate"])
            gevent.spawn_later(duration, runner.quit)

            runner.greenlet.join()

            # Generate and store report
            report = get_html_report(env, show_download_link=False, theme="light")

            asyncio.run(AskarStorage().update("report", session["client_id"], report))

        return render_template("index.jinja", form=form)

    @app.route("/report", methods=["GET", "POST"])
    def get_report():
        # Get latest client report
        report = asyncio.run(AskarStorage().fetch("report", session["client_id"]))
        if report:
            return report
        return {}, 404

    return app
