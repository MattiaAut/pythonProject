import requests
import os
import pathlib
import secrets
import sqlite3
import subprocess
import sys
import flask_mysqldb
from flask import Flask, session, abort, redirect, request, render_template, flash
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from datetime import timedelta
from flask import session, app

from flask_mysqldb import MySQL

secret_key = secrets.token_hex(16)
app = Flask("FrontlineCode", template_folder="templates")
app.config['SECRET_KEY'] = secret_key

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'FrontlineCode'

mysql = MySQL(app)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
#app.secret.key="CodeSpecialist.com"
GOOGLE_CLIENT_ID="412052900468-fmptddpq7os5ld3u9bbjpuvm6j35mf6q.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent,"client-secret.json")

flow= Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

conn = sqlite3.connect("frontlinecode.db") #CONNESSO
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            abort(401)  #Authorization required
        else:
            if session["username"] == "":
                abort(401)
            else:
                return function()
    return wrapper

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

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
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["email"] = id_info.get("email")
    session["name"] = id_info.get("name")
    session["photo"] = id_info.get("picture")
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT Username FROM USER WHERE USERemail = session["email"]''')
    table = cursor.fetchall()
    cursor.close()
    session["username"] = table.row[0]

    if session["username"] == NULL:
        return  redirect("/choose_username")

    return redirect("/protected_area")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
def index():
    return render_template('index.html')

    #cursor = mysql.connection.cursor()
    #if cursor:
        #cursor.execute(''' SELECT * FROM USER''')
        #table = cursor.fetchall()
        #print('\n Table Data:')
        #for row in table:
       #     print(row[0], end=" ")
      #      print(row[1], end=" ")
     #       print(row[2], end="\n")
    #    cursor.close()



@app.route("/choose_username")
def choose_username():
    return render_template('choose_username.html')

@app.route("/check_username", methods=['GET', 'POST'])
def check_username():
    error=None
    if request.method == 'POST':
        form_data=request.form.get("username")
    else:
        form_data=None

    cursor = mysql.connection.cursor()
    cursor.execute ('''SELECT COUNT (*) AS QUANTITY FROM USER WHERE USERNAME = form_data''')
    table = cursor.fetchall()
    cursor.close()
    if(table.row[0] > 0 ):      #se l username gia esiste va fatta la query
        error = "Username already used"
        return render_template("choose_username.html",error=error)
    else:
        session["username"] = form_data
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO USER VALUES (session["email"],session["username"],"1")''')
        mysql.connection.commit()
        cursor.close()
        #insert user into db
        return redirect("/protected_area")

@app.route("/protected_area")
@login_is_required
def protected_area():
    return render_template('protected_area.html',name=session["name"], picture=session["photo"], email=session["email"], username=session["username"])

@app.route("/gameNUMQUESTION")
def gameNUMQUESTION():
    if "google_id" not in session:
        abort(401)  # Authorization required
    else:
        if session["username"] == "":
            abort(401)
        else:
            return render_template('gameNUMQUESTION.html',name=session["name"], email=session["email"], picture=session["photo"],username=session["username"])

@app.route("/profile")
def profile():
    if "google_id" not in session:
        abort(401)  # Authorization required
    else:
        if session["username"] == "":
            abort(401)
        else:
            return render_template('profile.html',name=session["name"], email=session["email"], picture=session["photo"],username=session["username"])

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=5000)