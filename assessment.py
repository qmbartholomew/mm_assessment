import requests 
# Import both APP ID and APP KEY for use in functions/API calls
from secrets import APP_ID, APP_KEY
from collections import Counter

def call_edamam_api(query_food, health_trend, calorie_amount):
    # Use arguments to create request URL
    url = f"https://api.edamam.com/api/recipes/v2?type=public&q={query_food}&app_id={APP_ID}&app_key={APP_KEY}"
    # Save URL response in a variable
    edamam_response = requests.get(url)
    # Save list of recipes in a variable
    recipe_hits = edamam_response.json()['hits']
    # Initialize an empty list to store valid recipes
    valid_recipes = []
    # Loop through all recipes returned from API call
    for i, recipe in enumerate(recipe_hits):
        # Save relevant information from each recipe in variables 
        recipe = recipe['recipe']
        recipe_name = recipe['label']
        health_labels = recipe['healthLabels']
        calories = recipe['calories']
        # If the recipe has the requested health trend AND is under the specified calorie amount, create object and add to valid_recipes list
        if((health_trend in health_labels) and (calories < calorie_amount)):
            other_health_labels = health_labels
            valid_recipe_object = {
                "item_number": i,
                "name": recipe_name,
                "other_health_labels": other_health_labels,
                "calories": calories
            }
            valid_recipes.append(valid_recipe_object)
    # Return the valid_recipes list
    return valid_recipes

# Function that takes two health queries and one ingredient query and returns matching recipes
def health_ingredient_search(health1, health2, ingredient):
    # Use the given health and ingredient queries/arguments to build the URL
    # Can also use "q" as a query param instead of "tag"; "tag" returns 307 matching results, while "q" returns the max of 10000
    url = f'https://api.edamam.com/api/recipes/v2?type=public&health={health1}&health={health2}&tag={ingredient}&app_id={APP_ID}&app_key={APP_KEY}'
    res = requests.get(url)

    recipe_hits = res.json()['hits']
    recipe_count = res.json()['count']

    # Initialize empty list to store results, filter relevant information from hits
    recipe_list = []
    # Instructions ask for both list of recipes and the number of recipes. Return the value from the count attribute as the first value in the list,
    # as hits only returns a maximum of 20 recipes
    recipe_list.append(recipe_count)
    for i, recipe in enumerate(recipe_hits):
        recipe = recipe['recipe']
        recipe_name = recipe['label']
        health_labels = recipe['healthLabels']
        recipe_ingredients = recipe['ingredients']
        recipe_obj = {
            "name": recipe_name,
            "health_labels": health_labels,
            "ingredients": recipe_ingredients
        }
        recipe_list.append(recipe_obj)
    return recipe_list

def top_cal_recipe(arr):
    largest_cal_recipe = None
    largest_cal_num = 0
    for recipe in arr:
        if(recipe['calories'] > largest_cal_num):
            largest_cal_num = recipe['calories']
            largest_cal_recipe = recipe
    return largest_cal_recipe

# Finds the most popular health label(s) and returns a list containing them as well as the number of occurences
def most_popular_health_label(arr):
    # Build a list of health labels
    health = []
    for recipe in arr:
        health_labels = recipe['other_health_labels']
        health.append(health_labels)

    # Iterate through each list of health labels and map each label to the number of times it appears - creates a list of counter dictionaries containing each health label with a value of 1
    frequency = list(map(Counter, health))
    # Sum the number of times each label appears throughout all counter dictionaries
    popularity = {ingredient: sum([count[ingredient] for count in frequency]) for ingredient in {ingredient for count in frequency for ingredient in count}}

    # Initialize a list to store the most frequent/popular health labels
    popular_tags = []
    # Find the largest value in 'popularity' list, the highest label occurance
    # Add it as the first value in the list, for access in the main function
    popular_tags.append(max(popularity.values()))

    # Adding the most popular tags to the list
    for ingredient,value in popularity.items():
        # If the number of occurences is equal to the highest of all labels, add that label to popular_tags
        if value == max(popularity.values()):
            popular_tags.append(ingredient)

    return popular_tags


def main():
    #collect data from the api
    #return the number of chicken recepies that are in the 'Mediterranean' food trend & under 5000 calories
    res = call_edamam_api("chicken", "Mediterranean", 5000)
    print(f'There are {len(res)} chicken recipes within the Mediterranean food trend under 5000 calories')
    for recipe in res:
        print(f'{recipe["name"]} ({round(recipe["calories"])}) calories')

    top_cals = top_cal_recipe(res)
    print(f'\nThe Mediterranean chicken recipe with the most calories is {top_cals["name"]} with {round(top_cals["calories"])} calories')

    specific_recipes = health_ingredient_search('vegan', 'gluten-free', 'cilantro')

    # Print the number of recipes that are vegan, gluten-free, and have cilantro.
    print(f'\nThere are {specific_recipes[0]} recipes that are vegan, gluten-free, and contain cilantro. Some recipes:')
    # Print the recipes that match the search, skip the count value [first element]
    for recipe in specific_recipes[1:]:
        print(recipe["name"])

    popular_health_labels = most_popular_health_label(res)
    # Print the number of times the most popular health label/trend appears
    print(f'\nBONUS:\nThe following health label(s) are most popular and appear {popular_health_labels[0]} times:')
    # Print the label(s)/trend(s) that are the most popular, skip the count value [first element]
    for label in popular_health_labels[1:]:
        print(label)

if __name__ == "__main__":
    main()
