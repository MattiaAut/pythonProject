import requests
import os
import pathlib
import secrets
import sqlite3
import subprocess
import sys
import flask
import flask_mysqldb
import datetime
import google.auth.transport.requests
from flask import Flask, session, abort, redirect, request, render_template, flash, app
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from datetime import timedelta
from flask_mysqldb import MySQL
from jinja2 import Template

secret_key = secrets.token_hex(16)
app = Flask("FrontlineCode", template_folder="templates")

app.config['SECRET_KEY'] = secret_key
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'FrontlineCode'

mysql = MySQL(app)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
#app.secret.key="CodeSpecialist.com"
GOOGLE_CLIENT_ID="412052900468-fmptddpq7os5ld3u9bbjpuvm6j35mf6q.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent,"client-secret.json")
error ="no_error"

flow= Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

conn = sqlite3.connect("frontlinecode.db")  # CONNECTED

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            abort(401)  #Authorization required
        else:
            if session["username"] is None:
                abort(401)
            else:
                return function()
    return wrapper

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  #State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    #session.permanent = True    vedere come far scegliere all utente un altro account eliminando i cookie  session.clear non basta
    #app.permanent_session_lifetime = timedelta(minutes=1)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=0
    )

    session["google_id"] = id_info.get("sub")
    session["email"] = id_info.get("email")
    session["name"] = id_info.get("name")
    session["photo"] = id_info.get("picture")
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT Username FROM USER WHERE UserEmail ="%s"''' %session['email'])
    result = cursor.fetchone()
    cursor.close()
    if result is not None:
        session["username"] = result[0]
    else:
        return redirect("/choose_username")

    return redirect("/protected_area")

@app.route("/choose_username")
def choose_username():
    global error
    if error == "no_error":
        return render_template("choose_username.html")
    else:
        return render_template("choose_username.html", error=error)

@app.route("/check_username", methods=['GET', 'POST'])
def check_username():
    global error
    if request.method == 'POST':
        form_data = request.form.get("username")

    username_choosed = form_data
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT COUNT(*) AS QUANTITY FROM USER WHERE USERNAME = "%s"''' %username_choosed)
    result = cursor.fetchone()
    cursor.close()
    if result[0] > 0:
        error = "Username already used"
        return redirect("/choose_username")
    else:
        error="no_error"
        session["username"] = username_choosed
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO USER VALUES ("%s", "%s", 1)''' %(session["email"], session["username"]) )
        mysql.connection.commit()
        cursor.close()
        return redirect("/protected_area")


@app.route("/protected_area")
@login_is_required
def protected_area():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT COUNT(*) AS QUANTITY FROM QUESTION''')
    result = cursor.fetchone()
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT QuestionId, Difficulty , QuestionText FROM QUESTION''')
    list_of_tuples = cursor.fetchall()
    cursor.close()
    return render_template('protected_area.html',name=session["name"], picture=session["photo"], email=session["email"], username=session["username"], questions=result[0], value=list_of_tuples)

@app.route("/gameNUMQUESTION")
def gameNUMQUESTION():
    if "google_id" not in session:
        abort(401)  # Authorization required
    else:
        if session["username"] is None:
            abort(401)
        else:
            return render_template('gameNUMQUESTION.html',name=session["name"], email=session["email"], picture=session["photo"],username=session["username"])

@app.route("/profile")
def profile():
    if "google_id" not in session:
        abort(401)  # Authorization required
    else:
        if session["username"] is None:
            abort(401)
        else:
            return render_template('profile.html',name=session["name"], email=session["email"], picture=session["photo"],username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)