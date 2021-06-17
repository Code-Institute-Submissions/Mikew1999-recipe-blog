import os
from flask import (
    Flask, render_template, flash,
    request, redirect, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/log-in")
def log_in():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checks if username exists in db
        is_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # if user exists flash message and return to signup page
        if is_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        else:
            # pulls fields from form
            create_account = {
                "username": request.form.get("username").lower(),
                "fname": request.form.get("fname").lower(),
                "lname": request.form.get("lname").lower(),
                "email": request.form.get("email").lower(),
                "password": generate_password_hash(
                    request.form.get("password"))
            }
            # inserts new user info into users collection
            mongo.db.users.insert_one(create_account)

            # creates user session cookie
            session["user"] = request.form.get("username").lower()
            flash("Registration Successful!")
            return redirect(url_for("profile", username=session["user"]))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        is_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if is_user:
            if check_password_hash(
                is_user["password"],
                    request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))

            else:
                flash("Incorrect Password")
                return render_template("login")

    return render_template("login.html")


@app.route("/profile/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/recipes")
def recipe():
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


@app.route("/addrecipe", methods=["GET", "POST"])
def addrecipe():
    if request.method == "POST":
        recipes = mongo.db.recipes.find()
        recipemethod = mongo.db.recipemethod.find()

        recipe = {
            "recipeName": request.form.get("recipeName"),
            "serves": request.form.get("serves"),
            "cookingTime": request.form.get("cookingTime"),
            "prepTime": request.form.get("prepTime"),
            "ingredient1": request.form.get("ingredientName1"),
            "quantity1": request.form.get("quantity1"),
            "units1": request.form.get("units1"),
            "ingredient2": request.form.get("ingredientName2"),
            "quantity2": request.form.get("quantity2"),
            "units2": request.form.get("units2"),
            "ingredient3": request.form.get("ingredientName3"),
            "quantity3": request.form.get("quantity3"),
            "units3": request.form.get("units3"),
            "ingredient4": request.form.get("ingredientName4"),
            "quantity4": request.form.get("quantity4"),
            "units4": request.form.get("units4"),
            "ingredient5": request.form.get("ingredientName5"),
            "quantity5": request.form.get("quantity5"),
            "units5": request.form.get("units5"),
            "ingredient6": request.form.get("ingredientName6"),
            "quantity6": request.form.get("quantity6"),
            "units6": request.form.get("units6"),
            "ingredient7": request.form.get("ingredientName7"),
            "quantity7": request.form.get("quantity7"),
            "units7": request.form.get("units7"),
            "ingredient8": request.form.get("ingredientName8"),
            "quantity8": request.form.get("quantity8"),
            "units8": request.form.get("units8"),
            "ingredient9": request.form.get("ingredientName9"),
            "quantity9": request.form.get("quantity9"),
            "units9": request.form.get("units9"),
            "ingredient10": request.form.get("ingredientName10"),
            "quantity10": request.form.get("quantity10"),
            "units10": request.form.get("units10")
        }

        mongo.db.recipes.insert_one(recipe)

    return render_template(
        "recipes.html", recipes=recipes, recipemethod=recipemethod)


@app.route("/logout")
def logout():
    session.pop("user")
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
