from flask import Flask
import secrets
secret_key = secrets.token_hex(16)
app = Flask("FrontlineCode")
# example output, secret_key = 000d88cd9d90036ebdd237eb6b0db000
app.config['SECRET_KEY'] = secret_key
#app.secret.key="CodeSpecialist.com"
@app.route("/login")
def login():
    pass

@app.route("/callback")
def callback():
    pass

@app.route("/logout")
def logout():
    pass

@app.route("/")
def index():
    return "Mattia"

@app.route("/protected_area")
def protected_area():
    pass

if __name__ == "__main__":
    app.run(debug=True)
#ciao