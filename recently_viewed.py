''' Creates and returns recently viewed variable '''
import os

from flask import Flask, session
from flask_pymongo import PyMongo

if os.path.exists("env.py"):
    import env

app = Flask(__name__)
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# recently viewed
def recent():
    ''' Finds list of recently viewed recipes and returns list '''
    if not session.get('recently_viewed') is None:
        recently_viewed_recipes = []
        for item in session.get('recently_viewed'):
            recipe = mongo.db.recipes.find_one_or_404({'recipe_id': item})
            recently_viewed_recipes.append(recipe)
    else:
        recently_viewed_recipes = None

    context = {
        'recently_viewed_recipes': recently_viewed_recipes
    }

    return context
