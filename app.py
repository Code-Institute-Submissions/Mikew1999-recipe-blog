''' Main app routes '''
import os
from flask import (
    Flask, render_template, flash,
    request, redirect, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import smtplib
import ssl

from user_contexts import user_context
from recently_viewed import recent
if os.path.exists("env.py"):
    import env

from forms import LoginForm, RegisterForm, ChangePassword, ContactForm

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

categories = mongo.db.categories.find_one()
category_list = categories['categories']

# Recipe Search index
mongo.db.recipes.create_index(
    [
        ("recipeName", "text"),
        ("recipeDescription", "text"),
        ("author", "text")])


# function to retrieve file
@app.route('/file/<filename>')
def file(filename):
    ''' Returns file '''
    return mongo.send_file(filename)


# home page
@app.route("/", methods=['GET', 'POST'])
def index():
    ''' Home page '''
    # User contexts
    item = user_context()
    # Sets initial number of top recipes
    number = 3
    # Shows more recipes
    if request.method == "POST":
        if 'more_recipes' in request.form:
            number += 3

    top_recipes = mongo.db.recipes.find().limit(number).sort("likes", -1)

    return render_template(
        "index.html",
        user=item['user'],
        username=item['username'],
        top_recipes=top_recipes,
        list_of_liked_recipes=item['list_of_liked_recipes'],
        recently_viewed=recent()['recently_viewed_recipes']
    )


# sign up page
@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    ''' Renders signup page '''
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data.lower().strip()
        # checks if username exists in db
        is_user = mongo.db.users.find_one(
            {"username": username})

        # if user exists flash message and return to login page
        if is_user:
            flash("Username already exists")
            return redirect(url_for("log_in"))

        else:
            profile_image = form.profile_pic.data
            # checks if profile image has been selected
            if profile_image:
                # generates secure filename
                secured_image = secure_filename(profile_image.filename)
                # saves file to mongodb
                mongo.save_file(secured_image, profile_image)
            else:
                secured_image = 'None'

            # document to insert to users collection
            create_account = {
                "profileImageName": secured_image,
                "username": form.username.data.lower(),
                "fname": form.fname.data.lower(),
                "lname": form.lname.data.lower(),
                "email": form.email.data.lower(),
                "password": generate_password_hash(
                    password),
                "posts": [],
                "likedRecipes": [],
                "likedPosts": []
            }

            # inserts new user info into users collection
            mongo.db.users.insert_one(create_account)

            new_user = mongo.db.users.find_one({
                "username": request.form.get("username").lower()})

            # creates user session cookie
            session["user"] = new_user["username"]
            # flashes message to new user
            flash("Registration Successful!")
            return redirect(url_for(
                "profile",
                username=new_user["username"]))

    return render_template("signup.html", form=form)


# log in page
@app.route("/log-in", methods=["GET", "POST"])
def log_in():
    ''' Renders login page '''
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data.strip().lower()
        is_user = mongo.db.users.find_one(
            {"username": username})
        if is_user:
            users_password = is_user['password']
            if check_password_hash(users_password, password):
                session["user"] = username
                flash(f'Welcome {is_user["fname"]}!')
                return redirect(url_for("profile", username=session["user"]))
            else:
                flash("Incorrect username / password")
                return redirect(url_for("log_in"))
        else:
            flash("Incorrect username / password")
            return redirect(url_for("log_in"))
    return render_template("login.html", form=form)


# logs user out
@app.route("/logout")
def logout():
    ''' logs user out '''
    session.clear()
    return redirect(url_for('log_in'))


# profile page
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    ''' Renders profile page '''
    if session["user"]:
        # Recently viewed
        recently_viewed = recent()['recently_viewed_recipes']
        # grab the session users username from db
        item = user_context()
        user = item['user']
        user_recipes = mongo.db.recipes.find({"author": item['username']})

        profile_image = user['profileImageName']
        if profile_image == 'None':
            profile_image = None

        list_of_liked_recipes = []
        if item['list_of_liked_recipes'] is not None:
            for recipe_item in item['list_of_liked_recipes']:
                a_recipe = mongo.db.recipes.find_one(
                    {"recipeName": recipe_item})
                list_of_liked_recipes.append(a_recipe)

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
            recently_viewed=recently_viewed,
            profile_image=profile_image,
            my_posts=item['my_posts'],
            selected=selected,
            username=username,
            user_recipes=user_recipes,
            user=user,
            list_of_liked_recipes=list_of_liked_recipes)

    else:
        flash("Please login to view your profile")
        return render_template("login.html")


# changes users password
@app.route("/changepassword", methods=["GET", "POST"])
def change_password():
    ''' Changes users password '''
    form = ChangePassword()
    if form.validate_on_submit():
        username = form.username.data.lower()
        is_user = mongo.db.users.find_one({"username": username})
        password = request.form.get('password').strip().lower()
        confirm_new_password = form.confirm_password.data

        if str(password) == str(confirm_new_password):
            if is_user:
                users_email = is_user['email']
                email = form.email.data
                if str(email) == users_email:
                    mongo.db.users.update_one(
                        {"username": username}, {
                            "$set": {"password": str(
                                generate_password_hash(password))}})
                    session['user'] = form.username.data.lower()
                    flash("Password updated!")
                    return redirect(url_for(
                                    'profile',
                                    username=session['user']))
                else:
                    flash("Email address doesn't match our records")
                    return redirect(url_for('change_password'))

            else:
                flash(f'Username: {username} does not exist')
                return redirect(url_for('change_password'))

        else:
            flash("Password and Confirm new password boxes do not match!")
            return redirect(url_for('change_password'))

    return render_template('resetpassword.html', form=form)


# recipes page
@ app.route("/recipes", methods=["GET", "POST"])
def recipe():
    ''' Recipes page '''
    # User contexts
    user_info = user_context()
    user = user_info['user']
    list_of_liked_recipes = user_info['list_of_liked_recipes']

    if 'sort' in request.form:
        session['selected'] = request.form.get("sort")
        selected = request.form.get("sort")
    if not session.get("selected") is None:
        selected = session['selected']
    else:
        session['selected'] = 'likes'
        selected = 'recipe_id'

    recipes = mongo.db.recipes.find().sort(selected, -1)

    # initial variables
    results = recipes
    query = 'All Recipes'

    if request.method == "POST":
        if 'category' in request.form:
            query = request.form.get("category")
            results = mongo.db.recipes.find(
                {"categories": {"$all": [str(query)]}}).sort(selected, -1)
        elif 'toprecipes' in request.form:
            query = 'Top Recipes'
            results = mongo.db.recipes.find().limit(4).sort("likes", -1)
        else:
            # gets text input from search form
            query = request.form.get("q")

            # performs search
            search = ({"$text": {"$search": query}})
            # finds results
            results = mongo.db.recipes.find(search).sort(selected, -1)

        return render_template(
            "recipes.html",
            user=user,
            results=results,
            list_of_liked_recipes=list_of_liked_recipes,
            categories=categories,
            category_list=category_list,
            query=query)

    return render_template(
        "recipes.html",
        results=results,
        list_of_liked_recipes=list_of_liked_recipes,
        categories=categories,
        category_list=category_list,
        user=user,
        query=query)


# create recipe page
@ app.route("/createrecipe", methods=["GET", "POST"])
def create_recipe():
    ''' Creates recipe '''
    if not session.get('user') is None:
        if request.method == "POST":
            # finds username
            user = session['user']
            item = mongo.db.recipes.find().limit(1).sort("recipe_id", -1)
            for x in item:
                item_id = x['recipe_id']
            item_id += 1
            if 'recipeImage' in request.files:
                recipe_image = request.files['recipeImage']
                secured_image = secure_filename(recipe_image.filename)
                mongo.save_file(secured_image, recipe_image)

                # finds keys in form items dictionary
                form_keys = request.form.keys()

                # containers for keys and values
                ingredient_keys = []
                # contains ingredients inputted by user
                ingredient_values = []
                step_keys = []
                # contains steps inputted by user
                step_values = []
                # loops over keys in form items dictionary
                # where ingredient is in the key name
                for key in form_keys:
                    if "ingredient" in key:
                        ingredient_keys.append(key)
                    if "step" in key:
                        step_keys.append(key)

                for ingredient in ingredient_keys:
                    item = request.form.get(f'{ingredient}')
                    ingredient_values.append(str(item))

                for step in step_keys:
                    item = request.form.get(f'{step}')
                    step_values.append(str(item))

                recipe_details = {
                    "recipeImageName": secure_filename(recipe_image.filename),
                    "recipeName": request.form.get("recipeName"),
                    "serves": request.form.get("serves"),
                    "prepTime": request.form.get("prepTime"),
                    "cookingTime": request.form.get("cookingTime"),
                    "recipeDescription": request.form.get("recipeDescription"),
                    "likes": 0,
                    "author": user,
                    "ingredients": ingredient_values,
                    "steps": step_values,
                    "categories": request.form.getlist('category'),
                    'recipe_id': item_id,
                }

                mongo.db.recipes.insert_one(recipe_details)
        return render_template(
            "createrecipe.html",
            category_list=category_list)
    else:
        flash("Please login to create recipe")
        return redirect(url_for('log_in'))


# shows full recipe
@ app.route("/recipes/<recipe_name>", methods=['GET', 'POST'])
def view_recipe(recipe_name):
    ''' Full recipe '''
    item = user_context()
    selected_recipe = mongo.db.recipes.find_one({"recipeName": recipe_name})
    author = selected_recipe['author'].lower()

    if request.method == "POST":
        if 'edit_recipe' in request.form:
            can_edit_recipe = request.form.get("edit_recipe")
        else:
            can_edit_recipe = False
    else:
        can_edit_recipe = False

    user = item['user']
    list_of_liked_recipes = item['list_of_liked_recipes']
    all_categories = mongo.db.categories.find_one()
    category_list = all_categories['categories']

    # Adds recipe to recently viewed recipes session variable
    if not session.get('recently_viewed') is None:
        recently_viewed_recipes = session['recently_viewed']
        if selected_recipe['recipe_id'] not in recently_viewed_recipes:
            recently_viewed_recipes.append(selected_recipe['recipe_id'])
            session['recently_viewed'] = recently_viewed_recipes
    else:
        session['recently_viewed'] = [selected_recipe['recipe_id']]

    return render_template(
        "view_recipe.html",
        edit_recipe=can_edit_recipe,
        user=user,
        author=author,
        recipe_name=recipe_name,
        recipe=selected_recipe,
        category_list=category_list,
        list_of_liked_recipes=list_of_liked_recipes
    )


# like recipe
@ app.route("/recipes/<recipe_name>/<username>/like_recipe/",
            methods=["GET", "POST"])
def like(recipe_name, username):
    ''' likes / dislikes recipe '''
    if username == 'None':
        flash("Please Sign in to like / unlike recipe")
        return redirect(url_for('recipe'))
    else:
        user = mongo.db.users.find_one({"username": username})
        query = mongo.db.users.find_one({"likedRecipes": {"$exists": True}})
        selected_recipe = mongo.db.recipes.find_one(
            {"recipeName": recipe_name})
        likes = selected_recipe['likes']
        users_with_liked_recipes = mongo.db.users.find(query)

        if users_with_liked_recipes:
            users_liked_recipes = user['likedRecipes']
            if recipe_name not in users_liked_recipes:
                new_likes = likes + 1
                mongo.db.users.update_one({"username": username}, {
                    "$push": {"likedRecipes": recipe_name}})
                update_likes = {"$set": {"likes": new_likes}}
                flash("Liked recipe")
                mongo.db.recipes.update_one(selected_recipe, update_likes)
            else:
                new_likes = likes - 1
                mongo.db.users.update_one(
                    {"username": username}, {
                        "$pull": {"likedRecipes": recipe_name}})
                update_likes = {"$set": {"likes": new_likes}}
                mongo.db.recipes.update_one(selected_recipe, update_likes)
                flash("Unliked recipe")

        return redirect(url_for('view_recipe', recipe_name=recipe_name))


@ app.route("/recipes/<recipe_id>/edit_recipe", methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    ''' Edit recipe form handling '''
    selected_recipe = mongo.db.recipes.find_one_or_404(
        {"recipe_id": int(recipe_id)})
    if request.method == "POST":
        changes = {"$set": {}}
        steps = []
        ingredients = []
        recipe_categories = []
        recipe_name = selected_recipe['recipeName']

        for key, value in request.form.items():
            if 'step' in str(key):
                steps.append(str(value))
            elif 'ingredient' in str(key):
                ingredients.append(str(value))
            elif 'recipeDescription' in str(key):
                changes['$set']['recipeDescription'] = str(value).strip()
            elif 'category' not in str(key):
                if isinstance(value, int):
                    changes["$set"][str(key)] = int(value)
                else:
                    changes["$set"][str(key)] = str(value)

        if 'step' in request.form.keys():
            mongo.db.recipes.update_one(
                selected_recipe, {"$set": {"steps": []}})
            changes["$set"]['steps'] = steps

        if 'ingredient' in request.form.keys():
            mongo.db.recipes.update_one(
                selected_recipe, {"$set": {"ingredients": []}})
            changes["$set"]['ingredients'] = ingredients

        if 'category' in request.form.keys():
            mongo.db.recipes.update_one(
                selected_recipe, {"$set": {"categories": []}})
            selected_categories = request.form.getlist("category")
            for item in selected_categories:
                recipe_categories.append(str(item))
            changes["$set"]['categories'] = recipe_categories

        if 'recipeImage' in request.files:
            recipe_image = request.files['recipeImage']
            secured_image = secure_filename(recipe_image.filename)
            if secured_image != '':
                mongo.save_file(secured_image, recipe_image)
                changes["$set"]['recipeImageName'] = secured_image
        mongo.db.recipes.find_one_and_update(
            {"recipe_id": int(recipe_id)}, changes)
        recipe_name = mongo.db.recipes.find_one(
            {'recipe_id': int(recipe_id)})['recipeName']
        return redirect(url_for('view_recipe', recipe_name=recipe_name))
    return render_template('editrecipe.html', recipe=selected_recipe)


@app.route("/recipes/delete_recipe",
           methods=["GET", "POST"])
def delete_recipe():
    ''' Delete recipe '''
    if request.method == "POST":
        username = request.form.get('username')
        recipe_id = request.form.get('recipe_id')
        recipe_to_delete = mongo.db.recipes.find_one_and_delete(
            {"recipe_id": int(recipe_id)})
        recipe_name = recipe_to_delete['recipeName']
        image_name = secure_filename(recipe_to_delete['recipeImageName'])
        mongo.db.fs.files.delete_one({"filename": image_name})

        query = mongo.db.users.find()

        for item in query:
            mongo.db.users.update_many({}, {
                "$pull": {"likedRecipes": recipe_name}})
        session.clear()
        session['user'] = username
        flash("Recipe Deleted!")
        return redirect(url_for('index'))
    return redirect(url_for('recipe'))


@ app.route("/newsfeed/posts")
def posts():
    ''' Newfeed page '''
    all_posts = mongo.db.posts.find().sort("_id", -1)

    return render_template(
        "newsfeed.html",
        posts=all_posts)


@ app.route("/<username>/create_post", methods=["GET", "POST"])
def create_post(username):
    ''' Create post page '''
    if not session.get('user') is None:
        if username == 'None':
            flash("Please login to create post")
            return redirect(url_for('log_in'))
        if request.method == "POST":
            latest_post = mongo.db.posts.find_one(
                {"$query": {}, "$orderby": {"_id": -1}})
            if latest_post is None:
                new_post_id = 1
            else:
                post_id = latest_post['_id']
                new_post_id = post_id + 1

            post = {}

            for key, value in request.form.items():
                if 'postimage' not in str(key):
                    post[str(key)] = str(value)

            if 'postimage' in request.files:
                image = request.files['postimage']
                secured_image = secure_filename(image.filename)
                # saves file to mongodb
                mongo.save_file(secured_image, image)
                post['postimage'] = secured_image
            else:
                post['postimage'] = 'None'
            post['likes'] = 0
            post['comments'] = []
            post['author'] = username
            post["_id"] = new_post_id
            post['postid'] = new_post_id
            mongo.db.posts.insert_one(post)

            mongo.db.users.update_one({"username": username}, {
                "$addToSet": {"posts": new_post_id}})
            flash("Post Uploaded!")
            return redirect(url_for('index'))
        return render_template("createpost.html")
    else:
        flash("Please login to like create post")
        return redirect(url_for('log_in'))


@ app.route("/<username>/<posttitle>/edit_post", methods=["GET", "POST"])
def edit_post(username, posttitle):
    ''' Create post page '''
    if not session.get('user') is None:
        if username == 'None':
            flash("Please login to edit post")
            return redirect(url_for('log_in'))
        if request.method == "POST":
            post = mongo.db.posts.find_one_or_404(
                {"posttitle": request.form.get("posttitle")})
            updates = {}
            for key, value in request.form.items():
                if 'postimage' not in str(key):
                    updates[str(key)] = str(value)

            if 'postimage' in request.files:
                image = request.files['postimage']
                secured_image = secure_filename(image.filename)
                # saves file to mongodb
                mongo.save_file(secured_image, image)
                updates['postimage'] = secured_image
            else:
                updates['postimage'] = post['postimage']

            mongo.db.posts.update_one(
                post, {"$set": updates})
            flash("Post Updated!")
            return redirect(url_for('posts'))
        post = mongo.db.posts.find_one_or_404({"posttitle": posttitle})
        return render_template(
            "editpost.html",
            post=post)
    else:
        flash("Please login to like edit post")
        return redirect(url_for('log_in'))


# like post
@ app.route("/posts/<posttitle>/<username>/like_post/",
            methods=["GET", "POST"])
def like_post(posttitle, username):
    ''' Likes post '''
    if username == 'None':
        flash("Please Sign in to like recipe")
        return redirect(url_for('log_in'))
    else:
        if request.method == "POST":
            user = mongo.db.users.find_one({"username": username})
            post = mongo.db.posts.find_one({"posttitle": posttitle})
            if posttitle in user['likedPosts']:
                likes = post['likes']
                likes -= 1
                mongo.db.posts.update_one(post, {
                    "$set": {"likes": likes}
                })
                mongo.db.users.update_one(user, {
                    "$pull": {"likedPosts": posttitle}
                })
            else:
                if post['likes'] == 0:
                    likes = 1
                else:
                    likes = post['likes']
                    likes += 1
                mongo.db.posts.update_one(post, {
                    "$set": {"likes": likes}
                })
                mongo.db.users.update_one(user, {
                    "$addToSet": {"likedPosts": posttitle}})
        else:
            return redirect(url_for('posts'))
    return redirect(url_for('posts'))


@ app.route("/posts/<posttitle>/<username>/", methods=["GET", "POST"])
def post_comment(posttitle, username):
    ''' A view to handle the comment form '''
    if request.method == "POST":
        # Handles form input
        post = mongo.db.posts.find_one({"posttitle": posttitle})
        comment = {}
        comment['title'] = request.form.get("title")
        comment['comment'] = request.form.get("comment")
        comment['author'] = username

        mongo.db.posts.update_one(post, {
            "$addToSet": {
                "comments": comment
            }
        })
        flash("Comment Added!")
        return redirect(url_for('posts'))
    return redirect(url_for('posts'))


# edit profile picture
@app.route("/profile/<username>/edit_profile_picture",
           methods=["GET", "POST"])
def edit_profile_picture(username):
    ''' Edits profile pic '''
    user = mongo.db.users.find_one_or_404({"username": username})
    if request.method == "POST":
        if 'newProfilePic' not in request.files:
            flash("No file selected! Please select a file to upload.")
            return render_template("profile.html")

        else:
            # pulls new profile pic from form
            new = request.files['newProfilePic']
            if user['profileImageName'] == "None":
                secured_image = secure_filename(new.filename)
                # saves file to mongodb
                mongo.save_file(secured_image, new)
                mongo.db.users.update_one(user, {
                    "$set": {"profileImageName": secured_image}
                })
                flash("New Profile Pic uploaded!")
                return redirect(url_for('profile', username=username))
            else:
                old_profile_image = user['profileImageName']
                mongo.db.fs.files.delete_one({"filename": old_profile_image})
                secured_image = secure_filename(new.filename)
                # saves file to mongodb
                mongo.save_file(secured_image, new)
                mongo.db.users.update_one(user, {
                    "$set": {"profileImageName": secured_image}
                })
                flash("Profile image successfully changed!")
                return redirect(url_for('profile', username=username))
    return render_template("profile.html")


# deletes profile picture
@app.route("/profile/<username>/delete_profile_image",
           methods=["GET", "POST"])
def delete_profile_image(username):
    ''' Deletes profile pic '''
    # grabs users account
    user = mongo.db.users.find_one_or_404({"username": username})
    # finds profile image name
    profile_image = user['profileImageName']
    # finds profile image record
    file_image = mongo.db.fs.files.find_one({"filename": profile_image})
    # finds file_id
    file_id = file_image['_id']
    # deletes file from db
    mongo.db.fs.files.delete_one({"_id": file_id})

    # changes to update
    update = {"$set": {
        "profileImageName": "None"}}

    # updates hasProfileImage in users collection
    mongo.db.users.update_one(user, update)
    return redirect(url_for('profile', username=username))


# edits personal details
@ app.route("/profile/<username>/edit_personal_details",
            methods=["GET", "POST"])
def edit_personal_details(username):
    ''' Edits personal details '''
    if request.method == "POST":
        user = mongo.db.users.find_one_or_404({"username": username})
        new_email = request.form.get("email").lower()
        new_first_name = request.form.get("fname").lower()
        new_last_name = request.form.get("lname").lower()

        update = {"$set": {
            "email": new_email,
            "fname": new_first_name,
            "lname": new_last_name}}

        mongo.db.users.update_one(user, update)

        session.pop("user")
        session['user'] = username
        flash("Personal details updated successfully!")
        return redirect(url_for(
                        'profile',
                        username=username))
    else:
        return redirect(url_for(
                        'profile',
                        username=username))


# deletes profile pic
@ app.route("/profile/<username>/delete_profile", methods=["GET", "POST"])
def delete_profile(username):
    ''' Deletes profile '''
    if request.method == "POST":
        user_record = mongo.db.users.find_one_or_404({"username": username})
        # if user has profile picture
        if user_record['profileImageName'] != "None":
            profile_image = user_record['profileImageName']
            secure_image = secure_filename(profile_image)
            new_file = mongo.db.fs.files.find_one({"filename": secure_image})
            mongo.db.fs.files.delete_one(new_file)

        # finds list of user recipes
        for item in mongo.db.recipes.find():
            author = item['author']
            if author == username:
                update = {"$set": {"author": "User Deleted"}}
                mongo.db.recipes.update_many({"author": username}, update)

        for item in mongo.db.posts.find():
            author = item['author']
            if author == username:
                update = {"$set": {"author": "User Deleted"}}

        session.pop("user")
        mongo.db.users.delete_one(user_record)
        flash("Profile Successfully Deleted.")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('profile', username=username))


# Contact me page
@ app.route('/contact', methods=['GET', 'POST'])
def contact():
    ''' Contact me page '''
    form = ContactForm()

    if form.validate_on_submit():
        full_name = form.full_name.data
        username = form.username.data
        email = form.email.data
        message = form.message.data

        try:
            mongo.db.messages.insert_one({
                "full_name": full_name,
                "username": username,
                "email": email,
                "message": message
                })
            flash("Message sent!")
            return redirect(url_for('index'))
        except:
            flash("message not sent, please try again later or email mikewalters1234@gmail.com")
    return render_template('contact.html', form=form)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
