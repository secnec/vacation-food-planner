from planner_app.loginmanager import login_manager
from planner_app.forms import RegistrationForm
from flask import Blueprint, redirect, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import planner_app.dboperations as dbo
from planner_app.validators import validate_recipe, validate_trip

site = Blueprint("site", __name__, template_folder="templates")


@login_manager.user_loader
def load_user(user_id):
    return dbo.get_user_by_id(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/login")

@site.route("/")
def index():
    return render_template("index.html")

@site.route("/trips")
@login_required
def trips():
    results = dbo.get_trips()
    return render_template("trips.html", trips=results)

@site.route("/recipes")
@login_required
def recipes():
    results = dbo.get_recipes()
    return render_template("recipes.html", recipes=results)

@site.route("/new_trip",  methods=["GET", "POST"])
@login_required
def new_trip():
    if request.method == "POST":
        result = validate_trip(request)
        if result != True:
            p=1
            while True:
                if f"participantnames-{p}" not in request.values.keys():
                    break
                p += 1
            r=1
            while True:
                if f"recipeids-{r}" not in request.values.keys():
                    break
                r += 1
            return render_template("new_trip.html", alert=result, part_number = p, rec_number = r)  
        else:
            dbo.insert_trip(request)
            return redirect("/trips")
    return render_template("new_trip.html", part_number = 1, rec_number = 1)

@site.route("/new_recipe", methods=["GET", "POST"])
@login_required
def new_recipe():
    if request.method == "POST":
        result = validate_recipe(request)
        if result != True:
            i=1
            while True:
                if f"ingredientnames-{i}" not in request.values.keys():
                    break
                i += 1
            return render_template("new_recipe.html", alert=result, ing_number = i)  
        else:
            dbo.insert_recipe(request)
            return redirect("/recipes")
    return render_template("new_recipe.html", ing_number = 1)

@site.route("/register", methods=["GET", "POST"])
def register():
    alert = None
    form = RegistrationForm()
    if request.method == "POST" and form.validate:
        if form.password.data != form.confirmation.data:
            alert = "Password and confirmation don't match."
            return render_template("register.html", form=form, alert=alert)            
        user = dbo.get_user_by_username(form.username.data)
        if user:
            alert = "Username is already taken."
            return render_template("register.html", form=form, alert=alert)
        else:
            dbo.insert_user(form.username.data, generate_password_hash(form.password.data))
            return redirect("/login")
    return render_template("register.html", form=form)


@site.route("/login", methods=["GET", "POST"])
def login():
    alert = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = dbo.get_user_by_username(username)
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