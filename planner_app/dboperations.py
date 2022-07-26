from planner_app.db import db
from sqlalchemy.orm.exc import NoResultFound
from planner_app.user import User
from flask_login import current_user

def get_user_by_username(username):
    try:
        sql = 'SELECT id, username, password FROM "user" WHERE username=:username'
        result = db.session.execute(sql, {"username":username}).one()
        return User(result[0], result[1], result[2])
    except NoResultFound:
        return None

def get_user_by_id(user_id):
    try:
        sql = 'SELECT id, username, password FROM "user" WHERE id=:id'
        result = db.session.execute(sql, {"id":user_id}).one()
        return User(result[0], result[1], result[2])
    except NoResultFound:
        return None

def insert_user(username, password):
    sql = 'INSERT INTO "user" (username, password) VALUES (:username, :password)'
    db.session.execute (sql, {
        "username":username, 
        "password":password
        })
    db.session.commit()

def insert_recipe(request):
    portions = request.values.get("portions")
    recipesql = "INSERT INTO recipe (name, instructions, portions, is_secret, owner_id) VALUES (:name, :instructions, :portions, :is_secret, :owner_id) RETURNING id"
    recipe_id = db.session.execute (recipesql, {
        "name":request.values.get("name").strip(), 
        "instructions":request.values.get("instructions"),
        "portions":portions,
        "is_secret":request.values.get("is_secret"),
        "owner_id": current_user.id
        }).first()[0]
    db.session.flush()
    
    i = 0
    while True:
        if f"ingredientnames-{i}" not in request.values.keys():
            break
        name = request.values.get(f"ingredientnames-{i}").strip()
        amount = request.values.get(f"ingredientamounts-{i}").strip()
        measure = request.values.get(f"ingredientmeasures-{i}").strip()
        amount, measure = portion_amount(amount, portions, measure)
        ingredientsql = "INSERT INTO ingredient (name, measure) VALUES (:name, :measure) RETURNING id"
        ingredient_id = db.session.execute (ingredientsql, {
        "name":name, 
        "measure":measure,
        }).first()[0]

        linksql = "INSERT INTO recipe_ingredient (recipe_id, ingredient_id, amount) VALUES (:recipe_id, :ingredient_id, :amount)"
        db.session.execute (linksql, {
        "recipe_id":recipe_id, 
        "ingredient_id":ingredient_id,
        "amount":amount
        })
        db.session.flush()
        i += 1
    db.session.commit()

def portion_amount(amount, portions, measure):
    # Divides the amount into single-eater portions, and converts the measure to g/ml if possible.
    # e.g. thhe amounts in a recipe for four eaters (4 portions) should be divided by four
    try:
        amount = float(amount.replace(',', '.'))
        portions = float(portions.replace(',', '.'))
    except ValueError:
        print("Amount or portion cannot be converted to float. This should not happen.")
        return amount, measure
    factor = 1
    if convert_to_ml_or_g(measure):
        factor, measure = convert_to_ml_or_g(measure)
    amount = (factor * amount) / portions
    return amount, measure



def get_recipe_names_ids():
    recipes_sql = "SELECT id, name, is_secret, owner_id FROM recipe"
    recipes = db.session.execute(recipes_sql).fetchall()
    results = []
    for r in recipes:
        if r[2] == True and r[3] != current_user.id:
            continue
        results.append({
            'id': r[0],
            'name': r[1],
        })
    return results


def get_recipes():
    recipes_sql = "SELECT id, name, is_secret, owner_id, instructions, portions FROM recipe"
    recipes = db.session.execute(recipes_sql).fetchall()
    results = []
    for r in recipes:
        if r[2] == True and r[3] != current_user.id:
            continue
        sql = "SELECT ingredient.name, ingredient.measure, (recipe_ingredient.amount * :portions) FROM recipe_ingredient INNER JOIN ingredient ON recipe_ingredient.ingredient_id=ingredient.id WHERE recipe_ingredient.recipe_id=:id"
        ingredients = db.session.execute(sql, {"id":r[0], "portions":r[5]}).fetchall()
        results.append({
            'id': r[0],
            'name': r[1],
            'portions': r[5],
            'instructions': r[4],
            'ingredients': ingredients
        })
    return results

def insert_trip(request):
    tripsql = "INSERT INTO trip (name, is_secret, owner_id) VALUES (:name, :is_secret, :owner_id) RETURNING id"
    trip_id = db.session.execute (tripsql, {
        "name":request.values.get("name").strip(), 
        "is_secret":request.values.get("is_secret"),
        "owner_id": current_user.id
        }).first()[0]
    db.session.flush()
    
    i = 0
    while True:
        if f"participantnames-{i}" not in request.values.keys():
            break
        name = request.values.get(f"participantnames-{i}").strip()
        factor = request.values.get(f"participantfactors-{i}").replace(',','.').strip()

        participantsql = "INSERT INTO participant (name, factor) VALUES (:name, :factor) RETURNING id"
        participant_id = db.session.execute (participantsql, {
        "name":name, 
        "factor":factor,
        }).first()[0]

        trip_participantsql = "INSERT INTO trip_participant (trip_id, participant_id) VALUES (:trip_id, :participant_id)"
        db.session.execute (trip_participantsql, {
        "trip_id":trip_id, 
        "participant_id":participant_id,
        })
        db.session.flush()
        i += 1

    i = 0
    while True:
        if f"recipeids-{i}" not in request.values.keys():
            break
        recipe_id = request.values.get(f"recipeids-{i}").strip()
        if recipe_id == "":
            continue
        trip_recipesql = "INSERT INTO trip_recipe (trip_id, recipe_id) VALUES (:trip_id, :recipe_id)"
        db.session.execute (trip_recipesql, {
        "trip_id":trip_id, 
        "recipe_id":recipe_id,
        })
        db.session.flush()
        i += 1

    db.session.commit()


def get_trips():
    trips_sql = "SELECT id, name, is_secret, owner_id FROM trip"
    trips = db.session.execute(trips_sql).fetchall()
    results = []
    for r in trips:
        if r[2] == True and r[3] != current_user.id:
            continue
        participant_sql = "SELECT participant.name, participant.factor FROM trip_participant INNER JOIN participant ON trip_participant.participant_id=participant.id WHERE trip_participant.trip_id=:id"
        participants = db.session.execute(participant_sql, {"id":r[0]}).fetchall()
        factor_sum = 0
        for p in participants:
            factor_sum += p[1]
        recipe_sql = "SELECT recipe.name, recipe.portions FROM trip_recipe INNER JOIN recipe ON trip_recipe.recipe_id=recipe.id WHERE trip_recipe.trip_id=:id"
        recipes = db.session.execute(recipe_sql, {"id":r[0]}).fetchall()
        ingredients_sql="SELECT ingredient.name, recipe_ingredient.amount, ingredient.measure FROM trip_recipe INNER JOIN recipe_ingredient ON trip_recipe.recipe_id = recipe_ingredient.recipe_id INNER JOIN ingredient ON recipe_ingredient.ingredient_id = ingredient.id WHERE trip_recipe.trip_id=:id"
        ingredients = db.session.execute(ingredients_sql, {"id":r[0]}).fetchall()
        shopping_list = generate_shopping_list(ingredients, factor_sum)
        results.append({
            'id': r[0],
            'name': r[1],
            'participants': participants,
            'recipes': recipes,
            'shopping_list': shopping_list
        })
    return results

def generate_shopping_list(ingredients, factor_sum):
    shopping_dict = dict()
    for i in ingredients:
        name = i[0].capitalize()
        amount = i[1]
        measure = i[2].lower()
        amount = factor_sum*amount
        amount_list = shopping_dict.get(name)
        if amount_list == None:
            shopping_dict[name] = [(amount, measure)]
        else:
            measure_exists = False
            for a in range(len(amount_list)):
                if amount_list[a][1] == measure:
                    amount_list[a] = (amount_list[a][0]+amount, measure)
                    measure_exists = True
                    break
            if not measure_exists:
                amount_list.append((amount,measure))
            shopping_dict[name] = amount_list
    shopping_list = []
    for key, value in shopping_dict.items():
        item = key
        for i in range(len(value)):
            item += f' {value[i][0]} {value[i][1]}'
            if i < len(value)-1:
                item += ' + '
        shopping_list.append(item)
    return shopping_list


def convert_to_ml_or_g(measure):
    # Attempts to convert measures to g or ml 

    measure = measure.lower()
    factor = 0
    new_measure = ''
    if measure == 'l':
        factor =1000
        new_measure = 'ml'
    elif measure == 'dl':
        factor =100
        new_measure = 'ml'
    elif measure == 'cl':
        factor =10
        new_measure = 'ml'
    elif measure in ['tbsp','tbs', 'tb', 'rkl']:
        factor =15
        new_measure = 'ml'
    elif measure in ['tsp', 'ts', 'tl']:
        factor =5
        new_measure = 'ml'
    elif measure in ['cup', 'cups']:
        factor =236.6
        new_measure = 'ml'
    elif measure in ['fl oz', 'fl. oz.',  'oz. fl.', 'fluid ounce', 'fluid ounces']:
        factor =28.4
        new_measure = 'ml'
    elif measure == 'ml':
        factor =1
        new_measure = 'ml'
    elif measure in ['kg', 'kilo', 'kilos']:
        factor =1000
        new_measure = 'g'
    elif measure in ['g', 'gram']:
        factor =1
        new_measure = 'g'
    elif measure in ['ounce', 'ounces', 'oz', 'oz.']:
        factor =28.3
        new_measure = 'g'
    if factor == 0:
        return False
    else:
        return factor, new_measure


def check_recipe_id(id):
    try:
        sql = "SELECT name, is_secret, owner_id FROM recipe WHERE id=:id"
        result = db.session.execute(sql, {"id":id}).one()
        if result[1] == True and result[2] != current_user.id:
            return None
        return result
    except NoResultFound:
        return None