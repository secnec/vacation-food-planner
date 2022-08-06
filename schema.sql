CREATE TABLE "user"(id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT);
CREATE TABLE recipe(id SERIAL PRIMARY KEY, name TEXT, instructions TEXT, is_secret BOOLEAN DEFAULT True);
CREATE TABLE ingredient(id SERIAL PRIMARY KEY, name TEXT, measure TEXT);
CREATE TABLE recipe_ingredient(id SERIAL PRIMARY KEY, recipe_id INTEGER, ingredient_id INTEGER, amount FLOAT);