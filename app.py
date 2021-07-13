import os
from flask import (
    Flask, render_template, flash,
    request, redirect, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
if os.path.exists("env.py"):
    import env


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# home page
@app.route("/")
def index():
    return render_template("index.html")


# sign up page
@app.route("/signup")
def signup():
    return render_template("signup.html")


# sign up form handling
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checks if username exists in db
        is_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # if user exists flash message and return to login page
        if is_user:
            flash("Username already exists")
            return redirect(url_for("log_in"))

        else:
            profileImage = request.files['profilepic']
            # checks if profile image has been selected
            if profileImage:
                # generates secure filename
                securedImage = secure_filename(profileImage.filename)
                # saves file to mongodb
                mongo.save_file(securedImage, profileImage)

                # document to insert to users collection
                create_account = {
                    "profileImageName": securedImage,
                    "username": request.form.get("username").lower(),
                    "fname": request.form.get("fname").lower(),
                    "lname": request.form.get("lname").lower(),
                    "email": request.form.get("email").lower(),
                    "password": generate_password_hash(
                        request.form.get("password")),
                    "hasProfileImage": "1"}

                # inserts new user info into users collection
                mongo.db.users.insert_one(create_account)

                newUser = mongo.db.users.find_one({
                                    "username": request.form.get("username").lower()})
                hasProfilePic = newUser['hasProfileImage']
                # image variable to pass into profile page
                image = securedImage

                # creates user session cookie
                session["user"] = request.form.get("username").lower()
                # flashes message to new user
                flash("Registration Successful!")
                return redirect(url_for(
                                        "profile",
                                        username=session["user"],
                                        image=image,
                                        hasProfilePic=hasProfilePic))
            # if no profile image has been selected
            else:
                # document to insert to users collection
                create_account = {
                    "username": request.form.get("username").lower(),
                    "fname": request.form.get("fname").lower(),
                    "lname": request.form.get("lname").lower(),
                    "email": request.form.get("email").lower(),
                    "password": generate_password_hash(
                        request.form.get("password")),
                    "hasProfileImage": "0"}

                # inserts new user info into users collection
                mongo.db.users.insert_one(create_account)

                newUser = mongo.db.users.find_one({
                                    "username": request.form.get("username").lower()})
                hasProfilePic = newUser['hasProfileImage']
                # creates user session cookie
                session["user"] = request.form.get("username").lower()
                # flashes message to new user
                flash("Registration Successful!")
                return redirect(url_for(
                                        "profile",
                                        username=session["user"],
                                        hasProfilePic=hasProfilePic))

    return render_template("signup.html")


# log in page
@app.route("/log-in")
def log_in():
    return render_template("login.html")


# log in form handling
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


@app.route("/blog")
def blog():
    return render_template('blog.html')


# profile page
@app.route("/profile/<username>", methods=["GET"])
def profile(username):
    # grab the session users username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    user = mongo.db.users.find_one({"username": username})
    hasImage = str(user['hasProfileImage'])

    if session["user"]:
        if hasImage == "1":
            profileImage = user['profileImageName']
            return render_template(
                            "profile.html",
                            username=username,
                            profileImage=profileImage)
        else:
            return render_template(
                            "profile.html",
                            username=username,
                            hasImage=hasImage)

    return render_template("login.html")


# create recipe page
@app.route("/createrecipe")
def create_recipe():
    return render_template(
        "createrecipe.html")


# create recipe form handling
@app.route("/addrecipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        recipeList = mongo.db.recipes.find()
        recipes = mongo.db.recipes.find()

        if 'recipeImage' in request.files:
            recipeImage = request.files['recipeImage']
            securedImage = secure_filename(recipeImage.filename)
            mongo.save_file(securedImage, recipeImage)

            recipeDetails = {
                "recipeImageName": securedImage,
                "recipeName": request.form.get("recipeName"),
                "serves": request.form.get("serves"),
                "prepTime": request.form.get("prepTime"),
                "cookingTime": request.form.get("cookingTime"),
                "recipeDescription": request.form.get("recipeDescription")
            }

            _id = mongo.db.recipes.insert_one(recipeDetails).inserted_id

            ingredients = {
                "recipeName": request.form.get("recipeName"),
                "recipeID": _id,
                "ingredient1": request.form.get("ingredient1"),
                "ingredient2": request.form.get("ingredient2"),
                "ingredient3": request.form.get("ingredient3"),
                "ingredient4": request.form.get("ingredient4"),
                "ingredient5": request.form.get("ingredient5"),
                "ingredient6": request.form.get("ingredient6"),
                "ingredient7": request.form.get("ingredient7"),
                "ingredient8": request.form.get("ingredient8"),
                "ingredient9": request.form.get("ingredient9"),
                "ingredient10": request.form.get("ingredient10")
            }

            mongo.db.ingredients.insert_one(ingredients)

            steps = {
                "recipeName": request.form.get("recipeName"),
                "recipeID": _id,
                "step1": request.form.get("step1"),
                "step2": request.form.get("step2"),
                "step3": request.form.get("step3"),
                "step4": request.form.get("step4"),
                "step5": request.form.get("step5"),
                "step6": request.form.get("step6"),
                "step7": request.form.get("step7"),
                "step8": request.form.get("step8"),
                "step9": request.form.get("step9"),
                "step10": request.form.get("step10")
            }

            mongo.db.steps.insert_one(steps)

            recipes = mongo.db.recipes.find()

    return render_template(
                    "recipes.html",
                    recipeList=recipeList,
                    recipes=recipes,
                    mongo=mongo)


# function to retrieve file
@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


# recipes page
@app.route("/recipes")
def recipe():
    recipeList = mongo.db.recipes.find()
    recipes = mongo.db.recipes.find()

    return render_template(
                        "recipes.html",
                        recipeList=recipeList,
                        recipes=recipes,
                        mongo=mongo)


# logs user out
@app.route("/logout")
def logout():
    session.pop("user")
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
