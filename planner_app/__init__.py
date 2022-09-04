from flask import Flask
from os import getenv
from planner_app.routes import site
from planner_app.loginmanager import login_manager
from planner_app.db import db

def create_app(database_uri=None, secret_key=None):

    app = Flask(__name__)
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.secret_key = getenv("SECRET_KEY")

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if database_uri is None:
        app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace(
            "postgres://", "postgresql://"
        )
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    if secret_key is None:
        app.config["SECRET_KEY"] = getenv("SECRET_KEY")
    else:
        app.config["SECRET_KEY"] = secret_key

    db.init_app(app)
    login_manager.init_app(app)


    app.register_blueprint(site)

    return app


