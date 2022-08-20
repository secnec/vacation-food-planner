

def validate_recipe(request):
    result = True
    for key, value in request.args.items():
        if key == "name" and value == "":
            result = "Recipe name cannot be empty"
            break
        elif "ingredientnames" in key and value == "":
            result = "Ingredient name cannot be empty"
            break
        elif "ingredientamounts" in key:
            if value == "":
                result = "Ingredient amount cannot be empty"
                break
            if value.isnumeric() == False:
                result = "Ingredient amount has to be a number"
                break
        elif "ingredientmeasures" in key and value == "":
            result = "Ingredient measure cannot be empty"
            break
    return result

