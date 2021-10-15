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
categories = mongo.db.categories.find_one()
categoryList = categories['categories']


# log in page
@app.route("/log-in")
def log_in():
    ''' Renders login page '''
    return render_template("login.html")


# sign up page
@app.route("/signup")
def signup():
    ''' Renders signup page '''
    return render_template("signup.html")


# changes users password
@app.route("/changepassword", methods=["GET", "POST"])
def changePassword():
    ''' Changes users password '''
    if request.method == "POST":
        username = request.form.get("username").lower()
        isUser = mongo.db.users.find_one({"username": username})
        newPassword = request.form.get("password")
        confirmNewPassword = request.form.get("confirmNewPassword")

        if str(newPassword) == str(confirmNewPassword):
            if isUser:
                userRecord = isUser
                usersEmail = userRecord['email']
                email = request.form.get("email")
                if email == usersEmail:
                    print("email matches")
                    changes = {"$set": {"password": generate_password_hash(
                        request.form.get("password"))}}
                    mongo.db.users.update_one(userRecord, changes)
                    session['user'] = request.form.get("username").lower()
                    flash("Password updated!")
                    return redirect(url_for(
                                    'profile',
                                    username=session['user']))
                else:
                    flash("Email address doesn't match our records")
                    return redirect(url_for('resetPassword'))

            else:
                flash(f'Username: {username} does not exist')
                return redirect(url_for('resetPassword'))

        else:
            flash("Password and Confirm new password boxes do not match!")
            return redirect(url_for('resetPassword'))

    return redirect(url_for('resetPassword'))


# profile page
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    ''' Renders profile page '''
    # grab the session users username from db
    user = mongo.db.users.find_one_or_404({"username": username})
    user_recipes = mongo.db.recipes.find({"author": username})
    liked_recipes = user['likedRecipes']
    likes = user['likedRecipes']
    posts = mongo.db.posts.find()
    x = mongo.db.recipes.find_one

    if session["user"]:
        selected = 'personal_details'
        if 'personal_details' in request.form:
            selected = 'personal_details'
        if 'my_recipes' in request.form:
            selected = 'my_recipes'
        if 'liked_recipes' in request.form:
            selected = 'liked_recipes'
        if 'my_posts' in request.form:
            selected = 'my_posts'

        return render_template(
            "profile.html",
            selected=selected,
            liked_recipes=liked_recipes,
            username=username,
            likes=likes,
            user_recipes=user_recipes,
            posts=posts,
            x=x,
            user=user)

    else:
        flash("Please login to view your profile")
        return render_template("login.html")


# function to retrieve file
@app.route('/file/<filename>')
def file(filename):
    ''' Returns file '''
    return mongo.send_file(filename)


# home page
@app.route("/")
def index():
    ''' Home page '''
    top_recipes = mongo.db.recipes.find().limit(4).sort("likes", -1)
    if not session.get('user') is None:
        username = session['user']
        user = mongo.db.users.find_one({"username": username})
        if user['likedRecipes']:
            list_of_liked_recipes = user['likedRecipes']
        else:
            list_of_liked_recipes = None
    else:
        user = None
        list_of_liked_recipes = None

    return render_template(
        "index.html",
        user=user,
        username=username,
        top_recipes=top_recipes,
        list_of_liked_recipes=list_of_liked_recipes)


# recipes page
@app.route("/recipes", methods=["GET", "POST"])
def recipe():
    ''' Recipes page '''
    top_recipes = mongo.db.recipes.find().limit(4).sort("likes", -1)
    recipes = mongo.db.recipes.find()
    username = None
    if not session.get('user') is None:
        username = session['user']
        user = mongo.db.users.find_one({"username": username})
        if user['likedRecipes']:
            list_of_liked_recipes = user['likedRecipes']
        else:
            list_of_liked_recipes = None
    else:
        user = None
        list_of_liked_recipes = None

    if request.method == "POST":
        db = mongo.db.recipes
        mongo.db.recipes.create_index(
            [
                ("recipeName", "text"),
                ("recipeDescription", "text"),
                ("author", "text")])

        # gets text input from search form
        query = request.form.get("q")

        # performs search
        search = ({"$text": {"$search": query}})
        # finds results
        results = mongo.db.recipes.find(search)

        return render_template(
            "recipes.html",
            user=user,
            results=results,
            list_of_liked_recipes=list_of_liked_recipes,
            categories=categories,
            categoryList=categoryList,
            query=query,
            db=db)
    else:
        return render_template(
            "recipes.html",
            recipes=recipes,
            list_of_liked_recipes=list_of_liked_recipes,
            top_recipes=top_recipes,
            categories=categories,
            categoryList=categoryList,
            user=user,
            db=mongo.db.recipes)


# create recipe page
@app.route("/createrecipe")
def create_recipe():
    ''' Create recipe page '''
    return render_template(
        "createrecipe.html",
        categoryList=categoryList)


@app.route("/newsfeed/posts")
def posts():
    ''' Newfeed page '''
    posts = mongo.db.posts.find().sort("_id", -1)
    return render_template(
        "newsfeed.html",
        posts=posts)


@app.route("/newsfeed/posts/<post_id>", methods=["GET", "POST"])
def post_comment(post_id):
    ''' A view to handle the comment form '''
    user = session['user']
    if user:
        # Handles form input
        title = request.form.get('title')
        comment = request.form.get('comment')
        print(f'title: {title}, comment: {comment}')
    return redirect(url_for('posts'))


@app.route("/<username>/create_post", methods=["GET", "POST"])
def createPost(username):
    ''' Create post page '''
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
    ''' Likes post '''
    print(author)
    print(username)
    return redirect(url_for('newsFeed'))


# shows full recipe
@app.route("/recipes/<recipeName>")
def fullrecipe(recipeName):
    ''' Full recipe '''
    recipe = mongo.db.recipes.find_one({"recipeName": recipeName})
    author = recipe['author']
    user = mongo.db.users.find_one
    categories = recipe['categories']

    return render_template(
        "fullrecipe.html",
        user=user,
        categories=categories,
        author=author,
        recipeName=recipeName,
        recipe=recipe
    )


@app.route("/recipes/<recipeName>/edit_recipe")
def edit_recipe(recipeName):
    ''' edit recipe '''
    recipe = mongo.db.recipes.find_one({"recipeName": recipeName})
    x = mongo.db.users.find_one
    return render_template(
        "editrecipe.html",
        x=x,
        categoryList=categoryList,
        recipe=recipe)


@app.route("/recipes/<recipeName>/<username>/delete_recipe",
           methods=["GET", "POST"])
def deleteRecipe(recipeName, username):
    ''' Delete recipe '''
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
    ''' logs user out '''
    session.pop("user")
    return render_template("login.html")


@app.route("/view/<username>/profile")
def userProfile(username):
    ''' view to return selected users profile '''
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
    ''' Creates profile '''
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
    ''' Logs user in '''
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
    ''' Edits profile pic '''
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
    ''' Deletes profile pic '''
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
    ''' Edits personal details '''
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
    ''' likes / dislikes recipe '''
    if username == 'None':
        flash("Please Sign in to like / unlike recipe")
        return redirect(url_for('recipe'))
    else:
        user = mongo.db.users.find_one({"username": username})
        query = mongo.db.users.find_one({"likedRecipes": {"$exists": True}})
        recipe = mongo.db.recipes.find_one({"recipeName": recipeName})
        likes = recipe['likes']
        usersWithLikedRecipes = mongo.db.users.find(query)

        if usersWithLikedRecipes:
            usersLikedRecipes = user['likedRecipes']
            if recipeName not in usersLikedRecipes:
                newLikes = likes + 1
                mongo.db.users.update_one({"username": username}, {
                    "$push": {"likedRecipes": recipeName}})
                print("Updated liked recipes")
                updateLikes = {"$set": {"likes": newLikes}}
                mongo.db.recipes.update_one(recipe, updateLikes)
            else:
                newLikes = likes - 1
                mongo.db.users.update_one(
                    {"username": username}, {
                        "$pull": {"likedRecipes": recipeName}})
                updateLikes = {"$set": {"likes": newLikes}}
                mongo.db.recipes.update_one(recipe, updateLikes)

        return redirect(url_for('fullrecipe', recipeName=recipeName))


# create recipe form handling
@app.route("/addrecipe", methods=["GET", "POST"])
def add_recipe():
    ''' Creates recipe '''
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
    ''' Deletes profile '''
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


@app.route("/get_in_touch", methods=['GET', 'POST'])
def getInTouch():
    ''' Get in touch form '''
    if request.method == 'POST':
        full_name = str(request.form.get("full_name"))
        if 'username' in request.form:
            username = str(request.form.get("username"))
        else:
            username = None

        email = str(request.form.get("email"))
        message = str(request.form.get("message"))

        items = {
            'full_name': full_name,
            'username': username,
            'email': email,
            'message': message
        }

        session['email_items'] = items

        return redirect(url_for('contact_us'))

    else:
        return render_template(
            "contact.html")


@app.route("/contact")
def contact_us():
    ''' Sends an email '''
    email_items = session['email_items']

    return redirect(url_for('getInTouch'))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
