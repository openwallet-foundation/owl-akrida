from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from flask_avatars import Avatars
from .storage import AskarStorage
from locust.env import Environment
from locust.log import setup_logging
from locust.stats import stats_history, stats_printer
from locust.html import get_html_report
from wtforms import (
    StringField,
    IntegerRangeField,
    SubmitField,
    SelectField,
)
from wtforms.validators import InputRequired
from wtforms.widgets import RangeInput
# from wtforms.widgets import html5
import asyncio
import uuid
import hashlib
from locustfiles import LOCUST_FILES
import gevent

setup_logging("INFO")

def create_app():
    app = Flask(__name__)
    app.secret_key = str(uuid.uuid4())
    
    Avatars(app)

    class LocustConfigForm(FlaskForm):
        feature = SelectField("Feature", [InputRequired()])
        swarm_size = IntegerRangeField("Swarm Size", [InputRequired()], default=1)
        duration = IntegerRangeField("Duration", [InputRequired()], default=20)
        submit = SubmitField("Run")
        
    @app.before_request
    def before_request_callback():
        session['swarm_max'] = 10
        session['minutes_max'] = 5
        if 'client_id' not in session:
            session['client_id'] = hashlib.sha1(str(uuid.uuid4()).encode()).hexdigest()
            asyncio.run(AskarStorage().store('report', session['client_id'], {'message': 'Run your first test and your report will appear here!'}))

    @app.route("/", methods=["GET", "POST"])
    def index():
        form = LocustConfigForm()
        form.feature.choices = [
            (file_name, file_name) for file_name in LOCUST_FILES
        ]
        if request.method == 'POST':
            features = [form.feature.data]
            user_classes = [LOCUST_FILES[feature] for feature in features]
            swarm_size = form.swarm_size.data
            duration = form.duration.data
            spawn_rate = 1
            env = Environment(user_classes=user_classes)
            runner = env.create_local_runner()
            env.events.init.fire(environment=env, runner=runner)
            
            # gevent.spawn(stats_printer(env.stats))
            # gevent.spawn(stats_history, env.runner)
            runner.start(swarm_size, spawn_rate=spawn_rate)
            gevent.spawn_later(duration, runner.quit)
            
            runner.greenlet.join()
            report = get_html_report(env, show_download_link=False, theme="light")
            
            asyncio.run(AskarStorage().update('report', session['client_id'], report))

        return render_template('index.jinja', form=form)

    @app.route("/report", methods=["GET", "POST"])
    def get_report():
        report = asyncio.run(AskarStorage().fetch('report', session['client_id']))
        if report:
            return report
        return {}, 404
    
    return app
