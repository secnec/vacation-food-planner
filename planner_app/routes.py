from planner_app.db import db
from planner_app.loginmanager import login_manager
from planner_app.models import Ingredient, Recipe_ingredient, Recipe, User
from planner_app.forms import RecipeForm, RegistrationForm
from flask import Blueprint, redirect, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user


site = Blueprint("site", __name__, template_folder="templates")



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/login")

@site.route("/")
def index():
    return render_template("index.html")

@site.route("/trips")
@login_required
def trips():
    return render_template("trips.html")

@site.route("/recipes")
@login_required
def recipes():
    recipes = db.session.query(Recipe.id, Recipe.name, Recipe.instructions).filter_by(is_secret=False).all()
    results = []
    for r in recipes:
        sql = "SELECT ingredient.name, recipe_ingredient.amount FROM recipe_ingredient INNER JOIN ingredient ON recipe_ingredient.ingredient_id=ingredient.id WHERE recipe_ingredient.recipe_id=:id"
        ingredients = db.session.execute(sql, {"id":r.id}).fetchall()
        results.siteend({
            'name': r.name,
            'instructions': r.instructions,
            'ingredients': ingredients
        })
    return render_template("recipes.html", recipes=results)

@site.route("/new_trip")
@login_required
def new_trip():
    return render_template("new_trip.html")

@site.route("/new_recipe", methods=["GET", "POST"])
@login_required
def new_recipe():
    recipeform = RecipeForm()

    if request.method == "POST" and recipeform.validate:
        #name = request.form.get("name")
        #instructions = request.form.get("instructions")
        new_recipe = Recipe(
            name=recipeform.name.data,
            instructions=recipeform.instructions.data,
            is_secret = recipeform.is_secret.data
        )
        db.session.add(new_recipe)
        db.session.flush()
        db.session.refresh(new_recipe)

        for i in recipeform.ingredients.entries:
            new_ingredient = Ingredient(
                name=i.data,
                measure = "n/a"
            )
            db.session.add(new_ingredient)
            db.session.flush()
            db.session.refresh(new_ingredient)

            new_link = Recipe_ingredient(
                recipe_id = new_recipe.id,
                ingredient_id = new_ingredient.id,
                amount = "1"
            )
            db.session.add(new_link)
            db.session.flush()

        db.session.commit()
        #sql = "INSERT INTO recipe (name, instructions, is_secret) VALUES (:name, :instructions, :is_secret)"
        #db.session.execute(sql, {"name": name, "instructions": instructions, "is_secret": False})
        #db.session.commit()
        return redirect("/recipes")

    return render_template("new_recipe.html", form=recipeform)

@site.route("/register", methods=["GET", "POST"])
def register():
    alert = None
    form = RegistrationForm()

    if request.method == "POST" and form.validate:
        if form.password.data != form.confirmation.data:
            alert = "Password and confirmation don't match."
            return render_template("register.html", form=form, alert=alert)            

        user = (
            db.session.query(User.username).filter(User.username == form.username.data).first()
        )
        if user:
            alert = "Username is already taken."
            return render_template("register.html", form=form, alert=alert)
        
        else:
            new_user = User(
                username=form.username.data,
                password=generate_password_hash(form.password.data),
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
    return render_template("register.html", form=form)


@site.route("/login", methods=["GET", "POST"])
def login():
    alert = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user is None:
            alert = "Invalid username or password"
        elif check_password_hash(user.password, password):
            login_user(user)
            return redirect("/trips")
        else:
            alert = "Invalid username or password"

    return render_template("login.html", alert=alert)

@site.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")