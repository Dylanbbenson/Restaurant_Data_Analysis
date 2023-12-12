from yelpapi import YelpAPI
import requests
import pandas as pd
import json
import sys
import re
import warnings
import os
from datetime import date
import argparse

current_date = date.today().strftime('%Y-%m-%d')

def get_user_input():
    city = input("Enter the city name: ")
    state = input("Enter the state in abbreviation format (eg: Minnesota = MN) : ")
    return city, state

## Main script Logic
def main(city, state):
    city = city.replace(" ", "-")
    city = city.capitalize()
    city_state = city + ", " + state

    # authenticate requests with your Yelp API key
    #you'll have to obtain a Yelp Fusion API key and put it in a credentials.json file, or alternately uncomment below code
    #yelp_api = YelpAPI(<your_api_key_here>)

    with open('credentials.json') as f:
        credentials = json.load(f)
    api_key = credentials['yelp'] 
    yelp_api = YelpAPI(api_key)

    # make API call to search for businesses
    offsets = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700]
    dfs = []
    for offset in offsets:
        raw_data = yelp_api.search_query(term='restaurants', location=city_state, offset=offset, limit=50)
        df = pd.DataFrame(raw_data['businesses'])
        dfs.append(df)
    combined_df = pd.concat(dfs)

    # Reset the index, since it will have duplicate values
    df = combined_df.reset_index(drop=True)
    df.to_csv("./data/" + city + "_Restaurants_"+current_date+".csv")

    # data cleaning and transformation
    ######################################################
    #Fix transactions
    df = pd.read_csv("./data/"+city+"_Restaurants_"+current_date+".csv")
    df['transactions'] = df['transactions'].apply(lambda x: x.replace("[", "").replace("]", "").replace("'", ""))
    def fix_transactions(transactions):
        if transactions == 'delivery, pickup':
            return 'pickup, delivery'
        else:
            return transactions

    df["transactions"] = df["transactions"].apply(fix_transactions) 
    df['transactions'] = df['transactions'].fillna('none')

    #fix address
    df['location'] = df['location'].str.replace("'", "\"")
    df['location'] = df['location'].str.replace("None", "null")

    location_dict = []

    for location in df['location']:
        loc = json.loads(location)
        location_dict.append(loc)

    location_df = pd.DataFrame.from_dict(location_dict, orient='columns')
    df = pd.merge(df, location_df, left_index=True, right_index=True)

    #fix coordinates
    df['coordinates'] = df['coordinates'].str.replace("'", "\"")
    df['coordinates'] = df['coordinates'].str.replace("None", "null")

    coordinates_dict = []

    for coordinate in df['coordinates']:
        coord = json.loads(coordinate)
        coordinates_dict.append(coord)

    coordinates_df = pd.DataFrame.from_dict(coordinates_dict, orient='columns')
    df = pd.merge(df, coordinates_df, left_index=True, right_index=True)
    df = pd.DataFrame(df)

    #fix categories
    df['categories'] = df['categories'].str.replace("'", "\"")
    df['categories'] = df['categories'].str.replace("None", "null")

    category_dict = []

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

    for category in category_df['category']:
        cat = json.loads(category)
        category_dict.append(cat)

    category_df = pd.DataFrame.from_dict(category_dict, orient='columns')
    category_df = category_df.rename(columns={'alias': 'foodtype'}) 
    df = pd.merge(df, category_df, left_index=True, right_index=True)

    ######################################################

    df.to_csv("./data/" + city + "_Restaurants_"+current_date+".csv")
    os.remove("./data/categories_tmp.csv")
    
    print("Script Finished\n" f"City: {city}, State: {state}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Your script description.")
    parser.add_argument("--city", help="City name")
    parser.add_argument("--state", help="State abbreviation")
    args = parser.parse_args()

    if args.city and args.state:
        main(args.city, args.state)
    else:
        city, state = get_user_input()
        main(city, state)
