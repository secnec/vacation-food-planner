from planner_app.db import db
from sqlalchemy.orm.exc import NoResultFound
from planner_app.user import User

def get_user(username):
    pass

def get_user_object(user_id):
    try:
        sql = 'SELECT id, username, password FROM "user" WHERE id=:id'
        result = db.session.execute(sql, {"id":user_id}).fetchone()
        return User(result[0], result[1], result[2])
    except NoResultFound:
        return None

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
        amount = request.values.get(f"ingredientamounts-{i}")
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
            'name': r[1],
            'instructions': r[2],
            'ingredients': ingredients
        })
    return results