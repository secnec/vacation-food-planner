from flask import Flask
from os import getenv
from dotenv import load_dotenv
from flask_login import LoginManager


load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DATABASE_URL"] = getenv("DATABASE_URL").replace("postgres://", "postgresql://")


login_manager = LoginManager()
login_manager.init_app(app)

import planner_app.routes
