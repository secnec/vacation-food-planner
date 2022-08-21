from planner_app.db import db
from sqlalchemy.orm.exc import NoResultFound
from planner_app.user import User

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
    recipesql = "INSERT INTO recipe (name, instructions, is_secret) VALUES (:name, :instructions, :is_secret) RETURNING id"
    recipe_id = db.session.execute (recipesql, {
        "name":request.values.get("name"), 
        "instructions":request.values.get("instructions"),
        "is_secret":True
        }).first()[0]
    db.session.flush()
    
    i = 0
    while True:
        if f"ingredientnames-{i}" not in request.values.keys():
            break
        name = request.values.get(f"ingredientnames-{i}")
        amount = request.values.get(f"ingredientamounts-{i}").replace(',','.')
        measure = request.values.get(f"ingredientmeasures-{i}")

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

def get_recipes():
    recipes_sql = "SELECT id, name, instructions FROM recipe"
    recipes = db.session.execute(recipes_sql).fetchall()
    results = []
    for r in recipes:
        sql = "SELECT ingredient.name, ingredient.measure, recipe_ingredient.amount FROM recipe_ingredient INNER JOIN ingredient ON recipe_ingredient.ingredient_id=ingredient.id WHERE recipe_ingredient.recipe_id=:id"
        ingredients = db.session.execute(sql, {"id":r[0]}).fetchall()
        results.append({
            'id': r[0],
            'name': r[1],
            'instructions': r[2],
            'ingredients': ingredients
        })
    return results

def insert_trip(request):
    tripsql = "INSERT INTO trip (name, is_secret) VALUES (:name, :is_secret) RETURNING id"
    trip_id = db.session.execute (tripsql, {
        "name":request.values.get("name"), 
        "is_secret":True
        }).first()[0]
    db.session.flush()
    
    i = 0
    while True:
        if f"participantnames-{i}" not in request.values.keys():
            break
        name = request.values.get(f"participantnames-{i}")
        factor = request.values.get(f"participantfactors-{i}").replace(',','.')

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
        recipe_id = request.values.get(f"recipeids-{i}")
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
    trips_sql = "SELECT id, name FROM trip"
    trips = db.session.execute(trips_sql).fetchall()
    results = []
    for r in trips:
        participant_sql = "SELECT participant.name, participant.factor FROM trip_participant INNER JOIN participant ON trip_participant.participant_id=participant.id WHERE trip_participant.trip_id=:id"
        participants = db.session.execute(participant_sql, {"id":r[0]}).fetchall()
        factor_sum = 0
        for p in participants:
            factor_sum += p[1]
        recipe_sql = "SELECT recipe.name FROM trip_recipe INNER JOIN recipe ON trip_recipe.recipe_id=recipe.id WHERE trip_recipe.trip_id=:id"
        recipes = db.session.execute(recipe_sql, {"id":r[0]}).fetchall()
        ingredients_sql="SELECT ingredient.name, recipe_ingredient.amount, ingredient.measure FROM trip_recipe INNER JOIN recipe_ingredient ON trip_recipe.recipe_id = recipe_ingredient.recipe_id INNER JOIN ingredient ON recipe_ingredient.ingredient_id = ingredient.id WHERE trip_recipe.trip_id=:id"
        ingredients = db.session.execute(ingredients_sql, {"id":r[0]}).fetchall()
        shopping_dict = dict()
        for i in ingredients:
            name = i[0]
            amount = i[1]
            measure = i[2]
            factor = 1
            if convert_to_ml_or_g(measure):
                factor, measure = convert_to_ml_or_g(measure)
            amount = factor*factor_sum*amount
            amount_list = shopping_dict.get(name)
            if amount_list == None:
                shopping_dict[name] = [(amount, measure)]
            else:
                measure_exists = False
                for a in amount_list:
                    if a[1] == measure:
                        amount_list[i] = (a[0]+amount, measure)
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

        results.append({
            'id': r[0],
            'name': r[1],
            'participants': participants,
            'recipes': recipes,
            'shopping_list': shopping_list
        })
    return results



def convert_to_ml_or_g(m):
    m = m.lower()
    f = 0
    t = ''
    if m == 'l':
        f=1000
        t = 'ml'
    elif m == 'dl':
        f=100
        t = 'ml'
    elif m == 'cl':
        f=10
        t = 'ml'
    elif m in ['tbsp','tbs', 'tb', 'rkl']:
        f=15
        t = 'ml'
    elif m in ['tsp', 'tl']:
        f=5
        t = 'ml'
    elif m == 'cup':
        f=240
        t = 'ml'
    elif m == 'ml':
        f=1
        t = 'ml'
    elif m in ['kg', 'kilo']:
        f=1000
        t = 'g'
    elif m in ['g', 'gram']:
        f=1
        t = 'g'
    if f == 0:
        return False
    else:
        return f,t


def check_recipe_id(id):
    try:
        sql = 'SELECT name FROM recipe WHERE id=:id'
        result = db.session.execute(sql, {"id":id}).one()
        return result
    except NoResultFound:
        return None