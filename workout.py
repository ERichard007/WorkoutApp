# My Classes
from database import Database
from exceptions import UserDoesntExistException, UserExistsException

#------------------------------------------------------------------

# Other imports
from flask import Flask, render_template, session, redirect, request

#------------------------------------------------------------------

# Main app
app = Flask(__name__)
app.secret_key = "admin123" # Currently hardcoded, but need change

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

@app.route("/program_dashboard", methods=["GET"])
def program_dashboard():
    db = Database()
    workout_programs = db.retrieve_all_workout_programs()

    return render_template("program_dashboard.html", workout_programs=workout_programs, user_id=session.get("user_id"))

@app.route("/program", methods=["POST", "GET"])
def create_program():

    if request.method == "POST":
        db = Database()
        
        try:
            print(session.get("user_id"))
            new_workout_program = db.create_workout_program(
                name=request.form["program_name"],
                user_id=session.get("user_id"),
                description=request.form["program_desc"],
                currently_active=request.form["status"])
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"
            return render_template("program.html", error=error)
        
        return redirect(f"/program/{new_workout_program.id}")

    return render_template("program.html")

@app.route("/program/<program_id>", methods=["POST", "GET"])
def program(program_id):

    if request.method == "POST":
        db = Database()

        updated_program = db.update_workout_program(
            program_id=program_id,
            name=request.form["program_name"],
            description=request.form["program_desc"],
            currently_active=request.form["status"]
        )

        return render_template("program.html", program=updated_program, user_id=session.get("user_id"))

    db = Database()
    program = db.retrieve_workout_program_by_id(program_id)


    return render_template("program.html", program=program, user_id=session.get("user_id"))

#APIS ----------------------------------------------------------------------------------------------------------------

@app.route("/api/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login")

#------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)