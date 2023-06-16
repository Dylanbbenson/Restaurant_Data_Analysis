from yelpapi import YelpAPI
import requests
import pandas as pd
import json
import sys
import re
import warnings
from datetime import date

# take in command line arguments
city = sys.argv[1]
state = sys.argv[2]
current_date = date.today().strftime('%Y-%m-%d')

# input checking and modification
if city == '': 
    city = input("Enter the city name: ")

if state == '':
    state = input("Enter the state in abbreviation format (eg: Minnesota = MN) : ")

while len(state) != 2:
    print("Invalid state entry. Try again.")
    state = input("Please try again: ")

city = city.replace(" ", "-")
city = city.capitalize()
city_state = city + ", " + state

# authenticate your requests with your Yelp API key

#you'll have to obtain a Yelp Fusion API key and put it in a credentials.json file, or alternately uncomment below code
#yelp_api = YelpAPI(<your_api_key_here>)

with open('credentials.json') as f:
    credentials = json.load(f)

api_key = credentials['yelp'] 

yelp_api = YelpAPI(api_key)

# make API call to search for businesses
offsets = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450]
dfs = []
for offset in offsets:
    raw_data = yelp_api.search_query(term='restaurants', location=city_state, offset=offset, limit=50)
    df = pd.DataFrame(raw_data['businesses'])
    dfs.append(df)

# Concatenate them vertically
combined_df = pd.concat(dfs)

# Reset the index, since it will have duplicate values
df = combined_df.reset_index(drop=True)
df.to_csv("./data/" + city + "_Restaurants_"+current_date+".csv")

######################################################
# data cleaning and conversion
#fix address
df = pd.read_csv("./data/"+city+"_Restaurants_"+current_date+".csv")
df['location'] = df['location'].str.replace("'", "\"")
df['location'] = df['location'].str.replace("None", "null")

location_dict = []

# iterate through 'location' column and load the JSON data
for location in df['location']:
    loc = json.loads(location)
    location_dict.append(loc)

location_df = pd.DataFrame.from_dict(location_dict, orient='columns')
df = pd.merge(df, location_df, left_index=True, right_index=True)

#fix coordinates
df['coordinates'] = df['coordinates'].str.replace("'", "\"")
df['coordinates'] = df['coordinates'].str.replace("None", "null")

coordinates_dict = []

# iterate through 'location' column and load the JSON data
for coordinate in df['coordinates']:
    coord = json.loads(coordinate)
    coordinates_dict.append(coord)

coordinates_df = pd.DataFrame.from_dict(coordinates_dict, orient='columns')
df = pd.merge(df, coordinates_df, left_index=True, right_index=True)

#fix categories
df['categories'] = df['categories'].str.replace("'", "\"")
df['categories'] = df['categories'].str.replace("None", "null")

category_dict = []

# iterate through 'category' column and load the JSON data
for category in df['categories']:
    loc = json.loads(category)
    category_dict.append(loc)

category_df = pd.DataFrame.from_dict(category_dict, orient='columns')
category_df = category_df[0]
category_df = pd.DataFrame(category_df)
category_df = category_df.rename(columns={0: 'category'}) 

category_df.to_csv("./data/categories_tmp.csv")
category_df = pd.read_csv("./data/categories_tmp.csv")

category_df['category'] = category_df['category'].str.replace("'", "\"")
category_df['category'] = category_df['category'].str.replace("None", "null")

category_dict = []

# iterate through 'category' column and load the JSON data
for category in category_df['category']:
    cat = json.loads(category)
    category_dict.append(cat)

category_df = pd.DataFrame.from_dict(category_dict, orient='columns')
category_df = category_df.rename(columns={'alias': 'foodtype'}) 
df = pd.merge(df, category_df, left_index=True, right_index=True)

######################################################

df.to_csv("./data/" + city + "_Restaurants_"+current_date+".csv")