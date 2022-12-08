from flask import Flask, render_template
#ciao
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
app=Flask(__name__)
@app.route('/')
def index():
    return render_template("index.html")