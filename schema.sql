CREATE TABLE "user"(id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, username TEXT UNIQUE, password TEXT);
CREATE TABLE recipe(id SERIAL PRIMARY KEY, name TEXT, instructions TEXT, portions INTEGER, is_secret BOOLEAN DEFAULT True, owner_id INTEGER);
CREATE TABLE ingredient(id SERIAL PRIMARY KEY, name TEXT, measure TEXT);
CREATE TABLE recipe_ingredient(id SERIAL PRIMARY KEY, recipe_id INTEGER, ingredient_id INTEGER, amount FLOAT);
CREATE TABLE trip(id SERIAL PRIMARY KEY, name TEXT, is_secret BOOLEAN DEFAULT True, owner_id INTEGER);
CREATE TABLE participant(id SERIAL PRIMARY KEY, name TEXT, factor FLOAT);
CREATE TABLE trip_participant(id SERIAL PRIMARY KEY, trip_id INTEGER, participant_id INTEGER);
CREATE TABLE trip_recipe(id SERIAL PRIMARY KEY, trip_id INTEGER, recipe_id INTEGER);