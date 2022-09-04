# Planner for vacation menu 
This is a repository for my work on the Databases laboratory course of the University of Helsinki

## Application purpose
Groups going on vacation can use this application to plan their menu. The application will create a shopping list for the user.

## Description of core functionality
- User can create a new account, and log in
- A user can create a new trip in the application, and add the following entities:
    - Recipes for meals
        - Each recipe has ingredients linked to it
    - Participants, who each have a factor of how much they eat (e.g. a child might have factor of 0,5)
- User can choose for each created trip and recipe if it is private or public  
    - Ingredient is always public
- User can see public trips and recipes created by other users
- A shopping list is automatically generated for each trip
    - The shopping list lists out the quantities required of each ingredient for the recipes linked to the trip

## Database structure
The database has the following tables
- user
- trip
- trip_recipe (many-many)
- recipe
- recipe_ingredient (many-many)
- ingredient
- trip_participant (one-many)
- participant

## Status for the final submittal on September 4th 2022
The app is deployed to Heroku, and can be tested there:
https://vacation-food-planner.herokuapp.com/

All functionality described above has been implemented.

Development done in the last sprint:
- The CSRF vulnerability has been fixed
- Bug found in shopping list generation has been fixed
- Design has been improved with CSS
- Number of portions have been added to recipes
    - These are taken into account in shopping list calculations
    - Database schema has been updated accordingly