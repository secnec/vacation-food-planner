from planner_app.loginmanager import login_manager
from planner_app.forms import RegistrationForm
from flask import Blueprint, redirect, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user
from planner_app.dboperations import insert_recipe, get_user_object, get_recipes
from planner_app.validators import validate_recipe

site = Blueprint("site", __name__, template_folder="templates")


@login_manager.user_loader
def load_user(user_id):
    return get_user_object(user_id)

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
    results = get_recipes()
    print(results)
    return render_template("recipes.html", recipes=results)

@site.route("/new_trip")
@login_required
def new_trip():
    return render_template("new_trip.html")

@site.route("/new_recipe", methods=["GET", "POST"])
@login_required
def new_recipe():

    if request.method == "POST":
        result = validate_recipe(request)
        if result != True:
            return render_template("new_recipe.html", alert=result)  
        else:
            insert_recipe(request)
            return redirect("/recipes")

    return render_template("new_recipe.html")

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
        user, password = get_user(username)
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