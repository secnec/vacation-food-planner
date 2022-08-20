from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", 
        validators=[
            Length(min=4, message="Username must be at least four characters long."),
            DataRequired(message="Username cannot be empty")
            ])
    password = PasswordField(
        "Password", 
        validators=[
            Length(min=8, message="Password must be at least 8 characters long."),
            DataRequired(message="Password cannot be empty")
            ])
    confirmation = PasswordField(
        "Password confirmation"
        )