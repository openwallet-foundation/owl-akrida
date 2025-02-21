from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from storage import AskarStorage
from wtforms import (
    StringField,
    IntegerRangeField,
    SubmitField,
    SelectField,
)
from wtforms.validators import InputRequired
import asyncio
import uuid
# from locustfiles import LOCUST_FILES

LOCUST_FILES = {
    'AnonCredsIssue': 'AnonCredsIssue',
    'AnonCredsVerify': 'AnonCredsVerify',
    'AnonCredsRevoke': 'AnonCredsRevoke',
}

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

class LocustConfigForm(FlaskForm):
    feature = SelectField("Feature", [InputRequired()])
    swarm_size = IntegerRangeField("Swarm Size", [InputRequired()], default=1)
    # increment = IntegerRangeField("Swarm Size", [InputRequired()], default=1)
    # duration = IntegerRangeField("Duration", [InputRequired()], default=1)
    submit = SubmitField("Run")
    
@app.before_request
def before_request_callback():
    if 'client_id' not in session:
        session['client_id'] = str(uuid.uuid4())
        asyncio.run(AskarStorage().store('report', session['client_id'], {}))

@app.route("/", methods=["GET", "POST"])
def index():
    form = LocustConfigForm()
    form.feature.choices = [
        (file_name, file_name) for file_name in LOCUST_FILES
    ]
    if request.method == 'POST':
        report = {}
        asyncio.run(AskarStorage().update('report', session['client_id'], report))

    return render_template('index.jinja', form=form)

@app.route("/report", methods=["GET", "POST"])
def get_report():
    report = asyncio.run(AskarStorage().fetch('report', session['client_id']))
    if report:
        return report
    return {}, 404

if __name__ == "__main__":
    asyncio.run(AskarStorage().provision(recreate=False))
    app.run(host="0.0.0.0", port="5000", debug=True)
