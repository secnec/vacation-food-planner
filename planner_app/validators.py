from planner_app.dboperations import check_recipe_id
from re import match

def validate_recipe(request):
    for key, value in request.values.items():
        if key == "name" and value == "":
            return "Recipe name cannot be empty"
        elif key == "portions" and value == None or value == "":
            return "Portions cannot be empty"
        elif "ingredientnames" in key and value == "":
            return "Ingredient name cannot be empty"
        elif "ingredientamounts" in key:
            if value == "":
                return "Ingredient amount cannot be empty"
            if check_number_validity(value) is False:
                return "Ingredient amount has to be a positive number"
        elif "ingredientmeasures" in key and value == "":
            return "Ingredient measure cannot be empty"
    return True


def validate_trip(request):
    for key, value in request.values.items():
        if key == "name" and value == "":
            return "Trip name cannot be empty"
        elif "participantnames" in key and value == "":
            return "Participant name cannot be empty"
        elif "participantfactors" in key:
            if value == "":
                return "Participant factor cannot be empty"
            if check_number_validity(value) is False:
                return "Participant factor has to be a positive number"
        elif "recipeids" in key:
            if value.isnumeric() == False:
                return "Recipe id must be an integer"
            if  check_recipe_id(value) == None:
                return f"No recipe found with id {value}"
    return True

def check_number_validity(number):
    if match(r'^\d+(?:[\.,]\d+)$|^\d+$', number) is None:
        return False
    else:
        return True