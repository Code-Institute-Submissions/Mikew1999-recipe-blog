# Food Space

[View Live Project Here](https://mike-recipe-blog.herokuapp.com/) is a website for people who love food!

The main goals of the site are to allow users to view and share great recipes with others around the world. 

The site enables the user to create a profile, recipes, make social media style blog posts and view other users posts and recipes.

<!-- User Experience (UX) -->
# User Experience (UX)

* User Stories
    * First Time Visitor
        * As a First Time Visitor, I want to easily understand what this website is used for and why it should appeal to me.
            
        * As a First Time Visitor, I want the website to be easy and quick to navigate to the information/function that I need
            
        * As a First Time Visitor, I want to be able to browse the selection of recipes
        the website has to offer
            
        * As a First Time Visitor, I want to be able to browse for a specific user, perhaps one of their friends who uses the website.

        * As a First Time Visitor, I want to have the option to sign up for the website in order to post or like a recipe
        * As a First time visitor, I would like to be able to see the newsfeed pages

    * Returning Visitor Goals
        * As a returning visitor, I would like to view recipes I may have missed since last time I browsed the page
        * As a returning visitor, I would like to view new posts I may have missed since last time I browsed the page
        * As a returning visitor, I would like to be able to delete my profile
        * As a returning visitor, I would like to be able to delete my recipes
        * As a returning visitor, I would like to be able amend my personal details
        * As a returning visitor, I would like to be able amend my recipes
        * As a returning visitor, I would like to be able amend my posts
        * As a returning visitor, I would like to be able to see how many likes I have on my recipes and posts

    * Frequent Users Goals
        * As a frequent visitor, I would like to return often to check for new recipes
        * As a frequent visitor, I would like to upload recipes often
        * As a frequent visitor, I would like to be able to view how many likes my recipes and posts have

## Design

* Colour Scheme
    * The site is comprised of 2 colours: white and blue.
    The 2 colours provide good contrast for text and provides the white backgrounds provide a nice backdrop for images uploaded by the user. 
    
* Typography
    * For the typograpgy I have chosen to use some bootstrap classes (such as lead).
    * I have also selected to use the font family of "'sans-serif', Open Sans" and "'Open Sans', sans-serif"

* Imagery
    * I have chosen to use bright and eye-catching images to tempt the users tasebuds.
        This draws the user in and hopefully will attract them to keep coming back for more recipes

* Wireframes
    * Please see my [wireframes](wireframes/foodspacewireframes.pdf)

# Features

*   Fully Responsive on all device sizes - enables usability on all devices.
*   Login / signup functionality - Allows user to login and signup to view their own recipes e.t.c.
*   Reset Password functionality - Allows user to change their password if they forget.
*   Create Recipe functionality - Allows user to create Recipe
*   Delete Recipe - Allows user to delete recipe
*   Like / unlike recipe functionality - Allows user to like / unlike a recipe - this is used for returning top recipes
*   Shows top recipes based on number of likes - As above
*   Search recipes based on text input - Allows user to search for a recipe by text input
*   Search recipes based on category - Allows user to search for a recipe by selecting a category (e.g. vegerarian)
*   Search Users based on text input - Allows user to search for other user based on text input
*   View Users functionality - Allows user to view the Searched Users profile
*   Create Post functionality - Allows user to create a social media esque post
*   Edit Post - Allows user to edit post
*   View all posts - Allows user to see all posts
*   Log out functionality - Logs user out
*   Edit Profile Image - Allows user to edit their profile Image
*   Delete Profile Image - Allows user to delete their profile image
*   Delete Profile - Allows user to delete their profile (this doesn't remove the recipes as this would remove content from the site, as the user base builds up I will amend the function to delete all recipes uploaded by user)
*   Delete Recipe - Allows user to delete one of their recipes
*   Delete Post - Allows user to delete one of their posts

* Future Features
    * Scheduled deletion of files which don't have a fileID in fs.chunks (Didn't have time to implement)
    * Link recipes to 
 
# Technologies Used

## Languages Used

1.
    [HTML5](https://dev.w3.org/html5/html-author/) - HTML5 was used to render my website on the web
1.
    [CSS3](https://www.w3.org/Style/CSS/Overview.en.html) - CSS3 was used to style my HTML
1.
    [Python3](https://www.python.org/download/releases/3.0/) - Python3 was used for all back end processes such as form handling.

## Frameworks, Libraries & Programs Used

1.
    [Flask](https://flask.palletsprojects.com/en/2.0.x/) - Flask was used to render my pages and to generate URL's for each page
1.
    [Werkzeug](https://pypi.org/project/Werkzeug/) - Werkzeug was used for security features such as generating a password hash to not store plain passwords in db
1.
    [FlaskPymongo](https://flask-pymongo.readthedocs.io/en/latest/) - FlaskPymongo was used as a means of interacting with my database
1.
    [OS](https://docs.python.org/3/library/os.html) - OS was used to determine if my environment file (for configuring my mongodb settings e.t.c.) is present
1.
    [Jinja](https://jinja.palletsprojects.com/en/3.0.x/) - Jinja was used to write python inline, to loop over lists and arrays and to render my pages

# Data Models
The database for this project consists of:
1. Users collection
1. Recipes collection
1. Posts collection
1. File collections

The Users collection contains personal details of the user, their liked recipes, uploaded recipes and uploaded posts

The recipes collection contains all recipes and their author

The Posts collection contains all posts and their author

The collections are linked by a commonnality between them, for example recipe author = username.

# Testing

## Code Validity
* HTML Markup Validation - pass
    * All pages passed the validator when passing in full URL (except jinja)
* CSS Markup Validation - pass
    * All pages passed the validator when passing in full URL (except jinja)
* Python Validation - pass
    * app.py passed with no problems

## Testing user stories

* user stories testing 
    * The Page shows the user what can be done when first landing on page
                
    * The site is easy to navigate with several nav buttons
                
    * The site allows the user to browse recipes
                
    * The site allows the user to search users

    * The site allows the user to signup

    * The page allows the user to find new recipes

    * The site allows the user to find new posts
        
    * The site allows the user to delete their profile

    * The site allows the user to delete their recipes

    * The site allows the user to amend their personal details

    * The site allows the users to see how many likes the recipes have

    * The site allows the user to upload as many recipes as possible

    * The site allows the user to like recipe / post

    * The site allows the user to edit recipe / post

* functionality testing
    * The navbar is responsive on all devices and compressing nav works
    * search forms work 
    * Can edit posts, users profile and recipes
    * login, signup forms work perfectly - with and without profile pic
    * create recipe - works when logged in and reverts user to login page if not

The site was delevoped defensively so the site will not advise a user if it is their username / password which is incorrect

* performance testing
    * the site was tested on multiple browser (chrome and edge) and all functionality appears to be working. (some style issues on edge)
    * Logged in on multiple sessions at once with no reduction in responsivness


## Known Bugs
* Drop-downs don't work on internet explorer 
* Some style issues on edge

# Deployment

## Local

To run the app locally: 

1. Install dependancies by typing 'pip3 -r requirements.txt' into the terminal
1. Create environment file by typing 'touch env.py', enter environment variables (these are secret)
1. Run server locally by typing 'python3 app.py' into the terminal

## Heroku App

This website was deployed on Heroku App by following the below steps:

1.  Freeze dependancies into requirements file by typing 'pip3 freeze --local > requirements.txt'
1.  Create Procfile for Heroku by typing 'echo web: python app.py > Procfile'
1.  Create App on Heroku (signup to heroku, create app)
1.  Set deployment method to Github and connect profile
1.  Set environment variables via heroku app > settings > config vars
1.  Commit repository to github ('git add requirements.txt' then git commit -m "commit message", 'git add Procfile' then git commit -m "commit message" > git push)
1.  Enable automatic deployments via heroku app > deploy > enable automatic deployments

# Credits

## Code

I would like to thank [Pretty Printed](https://www.youtube.com/channel/UC-QDfvrRIDB6F0bIO4I4HkQ) for my understanding of saving and retrieving files from mongodb

## Content

I have used some recipes from [BBC Good Food](https://www.bbcgoodfood.com/recipes)
For the Ramen recipe - https://www.bbcgoodfood.com/recipes/super-quick-sesame-ramen

For the Carbonara - https://www.bbcgoodfood.com/recipes/ultimate-spaghetti-carbonara-recipe

For the tagliatelle - https://www.bbcgoodfood.com/recipes/speedy-sausage-stroganoff-tagliatelle

All rights go to their respective owners.

## Media

All media was sourced from [pixabay](https://pixabay.com/)

* Images:
    * carbonara.jpg - Image by [Wow Phochiangrak](https://pixabay.com/users/wow_pho-916237/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=712664)
    * chicken-319233_640.jpg - Image by [koisra](https://pixabay.com/users/koisra-137852/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=319233)
