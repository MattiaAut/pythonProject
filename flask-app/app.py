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
        cursor.execute('''INSERT INTO USER VALUES ("%s", "%s","2")''' %(session["email"], session["username"]) )
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
    cursor.execute('''SELECT QuestionId, Difficulty, QuestionText, QuestionTime FROM QUESTION''')
    list_of_tuples = cursor.fetchall()
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT Userrole FROM USER WHERE Useremail = "%s"''' %(session["email"]))
    role = cursor.fetchone()
    cursor.close()
    return render_template('protected_area.html', name=session["name"], picture=session["photo"], email=session["email"], username=session["username"], questions=result[0], value=list_of_tuples, role=role[0])

@app.route("/game", methods=['GET', 'POST'])
def game():
    if "google_id" not in session:
        abort(401)  # Authorization required
    else:
        if session["username"] is None:
            abort(401)
        else:
            if request.method == 'GET':
                form_data = request.values.get("level")
            level_choosed=form_data
            # search date from level choosed
            cursor = mysql.connection.cursor()
            cursor.execute('''SELECT Difficulty, QuestionText, QuestionCode, QuestionTime FROM QUESTION WHERE QuestionId = "%s"''' %level_choosed)
            list_of_tuples = cursor.fetchall()
            cursor.close()
            # search choose about quesion
            cursor = mysql.connection.cursor()
            cursor.execute(
                '''SELECT ChooseText FROM CHOOSE WHERE QuestionId = "%s"''' % level_choosed)
            choose = cursor.fetchall()
            cursor.close()
            return render_template('game.html', name=session["name"], email=session["email"], picture=session["photo"], username=session["username"], level=level_choosed, difficulty=list_of_tuples[0][0], question_text=list_of_tuples[0][1], question_code=list_of_tuples[0][2],question_time=list_of_tuples[0][3], choose=choose, time_spent=0)

@app.route("/gamesaved", methods=['GET', 'POST'])
def gamesaved():
    if "google_id" not in session:
        abort(401)  # Authorization required
    else:
        if session["username"] is None:
            abort(401)
        else:
            if request.method == 'POST':
                level = request.values.get("question_id")
                choose = request.values.get("choose")
                time = int(request.values.get("time"))

                cursor = mysql.connection.cursor()
                cursor.execute(
                    '''SELECT QuestionTime FROM QUESTION WHERE QuestionId="%s" ''' %level)
                question_time = cursor.fetchone()
                cursor.close()

                cursor = mysql.connection.cursor()
                cursor.execute(
                    '''SELECT Correct FROM CHOOSE WHERE QuestionId="%s" AND ChooseText = "%s"''' %(level, choose))
                result = cursor.fetchone()
                cursor.close()
                if(result == 1 and time>0):
                    score = 50
                    if(question_time - time > question_time/1.5):
                        score = score+50

                    if (question_time - time > question_time / 2):
                        score = score + 40

                    if (question_time - time > question_time / 2.5):
                        score = score + 30

                    if (question_time - time > question_time / 3):
                        score = score + 20

                    if (question_time - time > question_time ):
                        score = score + 10
                else:
                    score = 0

                cursor = mysql.connection.cursor()
                cursor.execute(
                    '''INSERT INTO PLAYS VALUES( "%s","%s","%s",CURRENT_DATE,"%s","%s")''' % (session["email"], level, score, choose, time )
                )
                mysql.connection.commit()
                cursor.close()
                return redirect("/protected_area")


@app.route("/profile")
def profile():
    if "google_id" not in session:
        abort(401)  # Authorization required
    else:
        if session["username"] is None:
            abort(401)
        else:
            return render_template('profile.html',name=session["name"], email=session["email"], picture=session["photo"],username=session["username"])
@app.route("/query")
def query():

    if "google_id" not in session:
        abort(401)  # Authorization required
    elif session["username"] is None:
        abort(401)
    else:
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT Userrole FROM USER WHERE Useremail = "%s"''' % (session["email"]))
        role = cursor.fetchone()
        cursor.close()
        if role[0] == 1:
            return render_template('query.html', name=session["name"], email=session["email"], picture=session["photo"], username=session["username"])

@app.route("/addchoose")
def addlevel():

    if "google_id" not in session:
        abort(401)  # Authorization required
    elif session["username"] is None:
        abort(401)
    else:
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT Userrole FROM USER WHERE Useremail = "%s"''' % (session["email"]))
        userrole1 = cursor.fetchone()
        cursor.close()
        if userrole1[0] == 1:
            return render_template('addchoose.html', name=session["name"], email=session["email"], picture=session["photo"], username=session["username"])

@app.route("/addquestion")
def addquestion():

    if "google_id" not in session:
        abort(401)  # Authorization required
    elif session["username"] is None:
        abort(401)
    else:
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT Userrole FROM USER WHERE Useremail = "%s"''' % (session["email"]))
        userrole2 = cursor.fetchone()
        cursor.close()
        if userrole2[0] == 1:
            return render_template('addquestion.html', name=session["name"], email=session["email"], picture=session["photo"], username=session["username"])
@app.route("/insertquestion", methods = ['GET','POST'])
def insertquestion():

    if "google_id" not in session:
        abort(401)  # Authorization required
    elif session["username"] is None:
        abort(401)
    else:
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT Userrole FROM USER WHERE Useremail = "%s"''' % (session["email"]))
        userrole4 = cursor.fetchone()
        cursor.close()
        if userrole4[0] == 1 and request.method == 'GET':
            questionid = request.values.get("questionid")
            questiontext = request.values.get("questiontext")
            questioncode = request.values.get("questioncode")
            correctoutput = request.values.get("correctoutput")
            questiontime = request.value.get("questiontime")
            difficulty = request.values.get("difficulty")
            cursor = mysql.connection.cursor()
            cursor.execute('''#INSERT INTO QUESTION VALUES ("%s","%s","%s","%s","%s","%s","%s","%s")''' %(questionid, questiontext, questioncode, correctoutput, datetime.date.today(), difficulty, session['email'], questiontime))
            cursor.close()
            return render_template('insertquestion.html', name=session["name"], email=session["email"], picture=session["photo"], username=session["username"])

@app.route("/insertchoose")
def insertchoose():

    if "google_id" not in session:
        abort(401)  # Authorization required
    elif session["username"] is None:
        abort(401)
    else:
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT Userrole FROM USER WHERE Useremail = "%s"''' % (session["email"]))
        userrole3 = cursor.fetchone()
        cursor.close()
        if userrole3[0] == 1:
            return render_template('insertchoose.html', name=session["name"], email=session["email"], picture=session["photo"], username=session["username"])
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)