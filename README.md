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
    - The public/private-status of a participant is inherited from the status of the trip it is linked to
- User can see public entities created by other users
- User can generate a shopping list for their trip
    - The shopping list lists out the quantities required of each ingredient for the recipes linked to the trip

## Database structure
The database will have the following tables
- user
- trip
- trip_recipe (many-many)
- recipe
- recipe_ingredient (many-many)
- ingredient
- trip_participant (one-many)
- participant

## Current status as of 21st August 2022
The app is deployed to Heroku, and can be tested there:
https://vacation-food-planner.herokuapp.com/

All functionality described above has been implemented.

Development to be done in the last sprint:
- Fixing any bugs found
- Stylistic improvements of code
- Improvements of UI and UX