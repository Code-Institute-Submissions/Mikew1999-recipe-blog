''' General Contexts to be imported into app.py '''
import os

from flask import Flask, session
from flask_pymongo import PyMongo

if os.path.exists("env.py"):
    import env

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# User Context
def user_context():
    ''' A function to return user details '''
    if not session.get('user') is None:
        username = session['user']
        user = mongo.db.users.find_one_or_404({"username": username})
        if user['likedRecipes']:
            list_of_liked_recipes = user['likedRecipes']
        else:
            list_of_liked_recipes = None
        my_posts = mongo.db.posts.find({"author": username})
    else:
        user = None
        username = None
        list_of_liked_recipes = None
        my_posts = None

    context = {
        'username': username,
        'user': user,
        'list_of_liked_recipes': list_of_liked_recipes,
        'my_posts': my_posts
    }

    return context
