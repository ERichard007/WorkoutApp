# My Classes
from database import Database
from exceptions import UserDoesntExistException, UserExistsException

#------------------------------------------------------------------

# Other imports
from flask import Flask, render_template, session, redirect, request, url_for
import os


#------------------------------------------------------------------

# Main app
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def home():
    db = Database()

    db.drop_tables()
    db.create_tables()

    if session.get("user_id"):
        return redirect("/program_dashboard")
    
    return redirect("/login")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = Database()

        try:
            user = db.get_user(username, password)
        except UserDoesntExistException:
            user = None

        if user:
            session["user_id"] = user.id
            return redirect("/program_dashboard")
        else:
            error = "Invalid username or password"
            return render_template("login.html", error=error)

    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = Database()

        try:
            db.create_user(username, password)
        except UserExistsException as e:
            error = str(e)
            return render_template("register.html", error=error)
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"
            return render_template("register.html", error=error)

        login = "Login with your new credentials!"
        return render_template("register.html", login=login)

    return render_template("register.html")


@app.route("/program_dashboard", methods=["POST", "GET"])
def program_dashboard():
    return render_template("program_dashboard.html")

#------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
