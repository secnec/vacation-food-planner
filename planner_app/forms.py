from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import TextArea

class RecipeForm(FlaskForm):
    name = StringField(
        "Recipe name", 
        validators=[DataRequired(message="Recipe name cannot be empty")]
        )
    instructions = StringField(
        "Preparation instructions",
        widget=TextArea()
        )
    ingredients = FieldList(StringField(
        '', 
        validators=[DataRequired(message="Ingredient name cannot be empty")]), 
        min_entries=1, 
        max_entries=15)
    is_secret = BooleanField("Make secret", validators=[DataRequired()])


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