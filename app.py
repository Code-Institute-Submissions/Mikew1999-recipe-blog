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

recipes = mongo.db.recipes.find()


# function to retrieve file
@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


# home page
@app.route("/")
def index():
    topRecipes = mongo.db.recipes.find().limit(3).sort("likes", -1)
    x = mongo.db.users.find_one

    return render_template(
        "index.html",
        x=x,
        topRecipes=topRecipes)


@app.route("/search", methods=["GET", "POST"])
def search():
    option = request.form.get("select")
    x = mongo.db.users.find_one
    if option == "recipes":
        # creates search index
        mongo.db.recipes.create_index(
            [
                ("recipeName", "text"),
                ("recipeDescription", "text"),
                ("author", "text")])

        # gets text input from search form
        query = request.form.get("search")

        # performs search
        search = ({"$text": {"$search": query}})
        # finds results
        results = mongo.db.recipes.find(search)

        return render_template(
            "searchedrecipes.html",
            results=results,
            query=query,
            x=x)

    else:
        mongo.db.users.create_index(
            [
                ("username", "text"),
                ("fname", "text"),
                ("lname", "text")])

        query = request.form.get("search")
        searchUser = ({"$text": {"$search": query}})

        results = mongo.db.users.find(searchUser)

        return render_template(
            "searcheduser.html",
            results=results,
            query=query)

    return url_for('index')


# sign up page
@app.route("/signup")
def signup():
    return render_template("signup.html")


# log in page
@app.route("/log-in")
def log_in():
    return render_template("login.html")


# reset password page
@app.route("/resetpassword")
def resetPassword():
    return render_template("resetpassword.html")


# changes users password
@app.route("/changepassword", methods=["GET", "POST"])
def changePassword():
    if request.method == "POST":
        # finds username from change password form
        username = request.form.get("username").lower()
        # finds if username exists in users collection
        isUser = mongo.db.users.find_one({"username": username})
        # new password
        newPassword = request.form.get("password")
        # confirm new password input
        confirmNewPassword = request.form.get("confirmNewPassword")

        # checks if newPassword input and confirmNewPassword
        # inputs match
        if str(newPassword) == str(confirmNewPassword):
            # checks if username exists
            if isUser:
                userRecord = isUser
                # finds users email address in db
                usersEmail = userRecord['email']
                # gets email address input
                email = request.form.get("email")
                # checks if email address matches email in users record
                if email == usersEmail:
                    # changes to update
                    changes = {"$set": {"password": generate_password_hash(
                        request.form.get("password"))}}
                    # updates password in users record
                    mongo.db.users.update_one(userRecord, changes)
                    # sets session cookie
                    session['user'] = request.form.get("username").lower()
                    # flashes message to user confirming their password
                    # has been updated
                    flash("Password updated!")
                    # sends the user to their profile page
                    return redirect(url_for(
                                    'profile',
                                    username=session['user']))
                    # if email address doesn't match

                else:
                    flash("Email address doesn't match our records")
                    return redirect(url_for('resetPassword'))

            # if user doesn't exist
            else:
                # flashes message to user
                flash(f'Username: {username} does not exist')
                return redirect(url_for('resetPassword'))

        # if password and confirm new password inputs don't match
        else:
            # flashes message to user
            flash("Password and Confirm new password boxes do not match!")
            # returns user to reset password page
            return redirect(url_for('resetPassword'))

    return redirect(url_for('resetPassword'))


# create recipe page
@app.route("/createrecipe")
def create_recipe():
    categories = mongo.db.categories.find_one()
    categoryList = categories['categories']
    return render_template(
        "createrecipe.html",
        categoryList=categoryList)


@app.route("/newsfeed/posts")
def posts():
    posts = mongo.db.posts.find().sort("_id", -1)
    return render_template(
        "posts.html",
        posts=posts)


@app.route("/<username>/create_post", methods=["GET", "POST"])
def createPost(username):
    if request.method == "POST":
        posts = mongo.db.posts.find().limit(1).sort("postID", -1)

        for post in posts:
            postID = post['_id']
            newPostID = postID + 1

        user = mongo.db.users.find_one({"username": username})

        if 'postimage' in request.files:
            image = request.files['postimage']
            securedImage = secure_filename(image.filename)
            # saves file to mongodb
            mongo.save_file(securedImage, image)
            post = {
                "_id": newPostID,
                "postimage": securedImage,
                "posttext": request.form.get("posttext"),
                "author": username
            }

            mongo.db.posts.insert_one(post)

            if user['hasPosted'] == "0":
                setHasPosted = {"$set": {"hasPosted": "1"}}
                mongo.db.users.update_one(user, setHasPosted)

            flash("Post Uploaded!")
            return redirect(url_for('index'))
        else:
            post = {
                "_id": newPostID,
                "posttext": request.form.get("posttext"),
                "author": username
            }

            mongo.db.posts.insert_one(post)

            if user['hasPosted'] == "0":
                setHasPosted = {"$set": {"hasPosted": "1"}}
                mongo.db.users.update_one(user, setHasPosted)

            flash("Post Uploaded!")
            return redirect(url_for('index'))

    return render_template("createpost.html")


# like post
@app.route("/posts/<author>/<username>/like_post/",
           methods=["GET", "POST"])
def likePost(author, username):
    print(author)
    print(username)
    return redirect(url_for('newsFeed'))


# recipes page
@app.route("/recipes")
def recipe():
    recipes = mongo.db.recipes.find()
    x = mongo.db.users.find_one
    categories = mongo.db.categories.find_one()
    categoryList = categories['categories']
    topRecipes = mongo.db.recipes.find().limit(2).sort("likes", -1)

    return render_template(
        "recipes.html",
        recipes=recipes,
        topRecipes=topRecipes,
        categories=categories,
        categoryList=categoryList,
        x=x)


@app.route("/recipes/categories/<categoryName>")
def category(categoryName):
    print(categoryName)
    x = mongo.db.recipes.find_one
    recipes = mongo.db.recipes.find()
    categories = mongo.db.categories.find_one()
    categoryList = categories['categories']

    results = mongo.db.recipes.find({"categories": categoryName})
    numberOfResults = results.count()

    return render_template(
        'searchedcategory.html',
        x=x,
        recipes=recipes,
        categories=categories,
        categoryList=categoryList,
        categoryName=categoryName,
        numberOfResults=numberOfResults,
        results=results
    )


@app.route("/recipes/signin")
def signInToLikeRecipe():
    flash("Please Sign in To Like recipe")
    return redirect(url_for('signup'))


# shows full recipe
@app.route("/recipes/<recipeName>")
def fullrecipe(recipeName):
    recipe = mongo.db.recipes.find_one({"recipeName": recipeName})
    author = recipe['author']
    x = mongo.db.users.find_one
    categories = recipe['categories']

    return render_template(
        "fullrecipe.html",
        x=x,
        categories=categories,
        author=author,
        recipeName=recipeName,
        recipe=recipe
    )


@app.route("/recipes/<recipeName>/edit_recipe")
def edit_recipe(recipeName):
    recipe = mongo.db.recipes.find_one({"recipeName": recipeName})
    x = mongo.db.users.find_one
    categories = mongo.db.categories.find_one()
    categoryList = categories['categories']
    return render_template(
        "editrecipe.html",
        x=x,
        categoryList=categoryList,
        recipe=recipe)


@app.route("/recipes/<recipeName>/<username>/delete_recipe",
           methods=["GET", "POST"])
def deleteRecipe(recipeName, username):
    recipes = mongo.db.recipes.find()
    user = mongo.db.users.find_one({"username": username})

    items = mongo.db.recipes.find_one_and_delete(
        {"$and": [{"author": username}, {"recipeName": recipeName}]})

    imageName = items['recipeImageName']

    mongo.db.fs.files.delete_one({"filename": imageName})

    if not mongo.db.recipes.find({"author": username}):
        update = {"$set": {"hasUploadedRecipe": "0"}}

        mongo.db.users.update_one(user, update)

    query = mongo.db.users.find_one({"likedRecipes": {"$exists": True}})
    usersWithLikedRecipes = mongo.db.users.find(query)

    if usersWithLikedRecipes:
        for x in usersWithLikedRecipes:
            usernames = x['username']
            mongo.db.users.update({"username": usernames}, {
                                  "$pull": {"likedRecipes": recipeName}})

            print(f'Username: {usernames}')
            print(f'Recipe Name: {recipeName}')

    return redirect(url_for('recipe', recipes=recipes))


# logs user out
@app.route("/logout")
def logout():
    session.pop("user")
    return render_template("login.html")


# profile page
@app.route("/profile/<username>", methods=["GET"])
def profile(username):
    # grab the session users username from db
    user = mongo.db.users.find_one({"username": username})
    allRecipes = mongo.db.recipes.find()
    userRecipes = mongo.db.recipes.find({"author": username})
    likedRecipes = user['likedRecipes']
    likes = user['likedRecipes']
    posts = mongo.db.posts.find()
    x = mongo.db.recipes.find_one

    if session["user"]:
        return render_template(
            "profile.html",
            likedRecipes=likedRecipes,
            username=username,
            likes=likes,
            allRecipes=allRecipes,
            userRecipes=userRecipes,
            posts=posts,
            x=x,
            user=user)

    else:
        flash("Please login to view your profile")
        return render_template("login.html")


@app.route("/view/<username>/profile")
def userProfile(username):
    user = mongo.db.users.find_one({"username": username})
    userRecipes = mongo.db.recipes.find({"author": username})
    likedRecipes = user['likedRecipes']
    x = mongo.db.recipes.find_one
    posts = mongo.db.posts.find()

    return render_template(
        "viewusersprofile.html",
        user=user,
        posts=posts,
        x=x,
        likedRecipes=likedRecipes,
        userRecipes=userRecipes)


# sign up function
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
                    "hasProfileImage": "1",
                    "hasUploadedRecipe": "0",
                    "hasPosted": "0",
                    "likedRecipes": []
                }

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
                    hasPosted="0",
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
                    "hasProfileImage": "0",
                    "hasUploadedRecipe": "0",
                    "hasPosted": "0",
                    "likedRecipes": []}

                # inserts new user info into users collection
                mongo.db.users.insert_one(create_account)

                newUser = mongo.db.users.find_one({
                    "username": request.form.get(
                        "username").lower()})
                hasProfilePic = newUser['hasProfileImage']
                # creates user session cookie
                session["user"] = request.form.get("username").lower()
                # flashes message to new user
                flash("Registration Successful!")
                return redirect(url_for(
                    "profile",
                    username=session["user"],
                    hasPosted="0",
                    hasProfilePic=hasProfilePic))

    return render_template("signup.html")


# log in function
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
                flash("Incorrect username / password")
                return redirect(url_for("log_in"))
        else:
            flash("Incorrect username / password")
            return redirect(url_for("log_in"))

    return redirect(url_for('log_in'))


# edit profile picture
@app.route("/profile/<username>/edit_profile_picture", methods=["GET", "POST"])
def edit_profile_picture(username):
    user = mongo.db.users.find_one({"username": username})
    if request.method == "POST":
        if 'newProfilePic' not in request.files:
            flash("No file selected! Please select a file to upload.")
            return render_template("profile.html")

        if 'newProfilePic' in request.files:
            user = mongo.db.users.find_one({"username": username})
            hasProfileImage = str(user['hasProfileImage'])
            # pulls new profile pic from form
            new = request.files['newProfilePic']

            # if user has a profile image
            if hasProfileImage == "1":
                # finds old profile image
                oldProfileImage = user['profileImageName']
                # deletes old profile image from fs.files
                mongo.db.fs.files.delete_one({"filename": oldProfileImage})

                # finds record where profile image name
                # matches oldProfileImage variable
                old = mongo.db.users.find_one(
                    {"profileImageName": oldProfileImage})

                # generates secure filename
                securedImage = secure_filename(new.filename)
                # saves file to mongodb
                mongo.save_file(securedImage, new)
                # new image
                image = securedImage

                # updates image to new image
                update = {"$set": {"profileImageName": image}}

                mongo.db.users.update_one(old, update)
                # flashes message to user
                flash("Profile image successfully changed!")
                return redirect(url_for('profile', username=username))

            # if user doesn't have a profile pic
            if hasProfileImage == "0":
                # generates secure filename
                securedImage = secure_filename(new.filename)
                value = "1"
                # saves file to mongodb
                mongo.save_file(securedImage, new)
                # info to update
                update = {"$set": {
                    "profileImageName": securedImage,
                    "hasProfileImage": value}}
                # updates profile image name to new profile image name
                mongo.db.users.update_one(user, update)
                # flashes message to user
                flash("Profile image successfully uploaded!")

                return redirect(url_for('profile', username=username))
    return render_template("profile.html")


# deletes profile picture
@app.route("/profile/<username>/delete_profile_image", methods=["GET", "POST"])
def deleteProfileImage(username):
    # grabs users account
    user = mongo.db.users.find_one({"username": username})
    # finds profile image name
    profileImage = user['profileImageName']
    # finds profile image record
    file = mongo.db.fs.files.find_one({"filename": profileImage})
    # finds file_id
    file_id = file['_id']
    # deletes file from db
    mongo.db.fs.files.delete_one({"_id": file_id})

    value = "0"
    # changes to update
    update = {"$set": {
        "hasProfileImage": value,
        "profileImageName": " "}}

    # updates hasProfileImage in users collection
    mongo.db.users.update_one(user, update)
    return redirect(url_for('profile', username=username))


# edits personal details
@app.route("/profile/<username>/edit_personal_details",
           methods=["GET", "POST"])
def editPersonalDetails(username):
    user = mongo.db.users.find_one({"username": username})
    newEmail = request.form.get("email").lower()
    newFirstName = request.form.get("fname").lower()
    newLastName = request.form.get("lname").lower()

    update = {"$set": {
        "email": newEmail,
        "fname": newFirstName,
        "lname": newLastName}}

    mongo.db.users.update_one(user, update)

    session.pop("user")
    session['user'] = request.form.get("username").lower()

    return redirect(url_for(
                    'profile',
                    username=request.form.
                    get("username").lower()))


# like recipe
@app.route("/recipes/<recipeName>/<username>/like_recipe/",
           methods=["GET", "POST"])
def like(recipeName, username):
    user = mongo.db.users.find_one({"username": username})
    query = mongo.db.users.find_one({"likedRecipes": {"$exists": True}})
    recipe = mongo.db.recipes.find_one({"recipeName": recipeName})
    likes = recipe['likes']
    newLikes = likes + 1

    usersWithLikedRecipes = mongo.db.users.find(query)

    if usersWithLikedRecipes:
        print("usersWithLikedRecipes is true")
        usersLikedRecipes = user['likedRecipes']
        if recipeName not in usersLikedRecipes:
            print("user not yet liked this recipe")
            mongo.db.users.update_one({"username": username}, {
                                      "$push": {"likedRecipes": recipeName}})
            print("Updated liked recipes")
            updateLikes = {"$set": {"likes": newLikes}}
            mongo.db.recipes.update_one(recipe, updateLikes)
            print("updated recipes to add 1 like")

    return redirect(url_for('fullrecipe', recipeName=recipeName))


# unlike recipe
@app.route("/recipes/<recipeName>/<username>/unlike_recipe",
           methods=["GET", "POST"])
def unlike(recipeName, username):
    user = mongo.db.users.find_one({"username": username})
    query = mongo.db.users.find_one({"likedRecipes": {"$exists": True}})
    recipe = mongo.db.recipes.find_one({"recipeName": recipeName})
    likes = recipe['likes']
    newLikes = likes - 1

    usersWithLikedRecipes = mongo.db.users.find(query)

    if usersWithLikedRecipes:
        print("usersWithLikedRecipes is true")
        usersLikedRecipes = user['likedRecipes']
        if recipeName in usersLikedRecipes:
            print("user has liked this recipe")
            mongo.db.users.update_one({"username": username}, {
                                      "$pull": {"likedRecipes": recipeName}})
            print("Updated liked recipes")
            updateLikes = {"$set": {"likes": newLikes}}
            mongo.db.recipes.update_one(recipe, updateLikes)
            print("updated recipes to deduct 1 like")

    return redirect(url_for('fullrecipe', recipeName=recipeName))


# create recipe form handling
@app.route("/addrecipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        # finds username
        user = session['user']
        # finds users record
        userRecord = mongo.db.users.find_one({"username": user})
        # amend hasUploaded Recipe value on users record
        setHasUploadedRecipe = {"$set": {"hasUploadedRecipe": "1"}}

        if 'recipeImage' in request.files:
            mongo.db.users.update_one(userRecord, setHasUploadedRecipe)

            recipeImage = request.files['recipeImage']
            securedImage = secure_filename(recipeImage.filename)
            mongo.save_file(securedImage, recipeImage)

            # finds keys in form items dictionary
            formKeys = request.form.keys()

            # containers for keys and values

            ingredientKeys = []
            # contains ingredients inputted by user
            ingredientValues = []

            stepKeys = []
            # contains steps inputted by user
            stepValues = []

            # loops over keys in form items dictionary
            # where ingredient is in the key name
            for key in formKeys:
                if "ingredient" in key:
                    ingredientKeys.append(key)
                if "step" in key:
                    stepKeys.append(key)

            for ingredient in ingredientKeys:
                a = request.form.get(f'{ingredient}')
                ingredientValues.append(str(a))

            for step in stepKeys:
                a = request.form.get(f'{step}')
                stepValues.append(str(a))

            recipeDetails = {
                "recipeImageName": securedImage,
                "recipeName": request.form.get("recipeName"),
                "serves": request.form.get("serves"),
                "prepTime": request.form.get("prepTime"),
                "cookingTime": request.form.get("cookingTime"),
                "recipeDescription": request.form.get("recipeDescription"),
                "likes": 0,
                "author": user,
                "ingredients": ingredientValues,
                "steps": stepValues,
                "categories": request.form.getlist('category')
            }

            mongo.db.recipes.insert_one(recipeDetails)

    return redirect(url_for('recipe'))


# deletes profile pic
@app.route("/profile/<username>/delete_profile", methods=["GET", "POST"])
def deleteProfile(username):
    userRecord = mongo.db.users.find_one({"username": username})
    # if user has profile picture
    if userRecord['hasProfileImage'] == "1":
        # deletes profile image data from fs.files in db
        profileImage = userRecord['profileImageName']
        securedImage = secure_filename(profileImage)
        file = mongo.db.fs.files.find_one({"filename": securedImage})
        mongo.db.fs.files.delete_one(file)

    # checks if user has uploaded recipes
    if userRecord['hasUploadedRecipe'] == "1":
        # finds list of user recipes
        for recipe in mongo.db.recipes.find():
            author = recipe['author']
            if author == username:
                update = {"$set": {"author": "User Deleted"}}
                mongo.db.recipes.update_many({"author": username}, update)

    session.pop("user")
    mongo.db.users.delete_one(userRecord)
    flash("Profile Successfully Deleted.")
    return redirect(url_for('index'))


# Searches recipes
@app.route("/recipes/search_recipes", methods=["GET", "POST"])
def searchRecipes():
    x = mongo.db.users.find_one
    # creates search index
    mongo.db.recipes.create_index(
        [
            ("recipeName", "text"),
            ("recipeDescription", "text"),
            ("author", "text")])

    # gets text input from search form
    query = request.form.get("search")
    # performs search
    search = ({"$text": {"$search": query}})
    # finds results
    results = mongo.db.recipes.find(search)

    return render_template(
        "searchedrecipes.html",
        x=x,
        results=results)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
