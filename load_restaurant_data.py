import pandas as pd
import numpy as np
import mysql.connector
from datetime import date
import sys
import argparse
from decouple import config
from dotenv import load_dotenv

load_dotenv(dotenv_path='config.env')
current_date = date.today().strftime('%Y-%m-%d')

def get_user_input():
    city = input("Enter the City: ")
    state = input("Enter the State: ")
    return city, state

def main(city, state):
    
    #establish DB connection
    def create_mysql_connection():
        connection = mysql.connector.connect(
            host=config('DB_HOST'),
            user=config('DB_USER'),
            password=config('DB_PASSWORD'),
            database=config('DB_NAME')
        )
        return connection

    # Load data into table
    def load_data_to_mysql(data, connection):
        cursor = connection.cursor()
        columns = ", ".join(data.columns)
        values = ", ".join(["%s" for _ in range(len(data.columns))])

        for index, row in data.iterrows():
            insert_query = f"INSERT INTO Business.restaurants ({columns}) VALUES ({values})"
            cursor.execute(insert_query, tuple(row))

        connection.commit()
        cursor.close()

    # Perform some data transformation
    df = pd.read_csv("./data/"+city+"_Restaurants_"+current_date+".csv")
    df = df[['name', 'review_count', 'rating', 'transactions', 'price', 'phone', 'display_phone', 'display_address', 'latitude', 'longitude', 'foodtype', 'city', 'state', 'country']]
    df = df.rename(columns={'display_address': 'address'}) 
    df['address'] = df['address'].apply(lambda x: x.replace("[", "").replace("]", "").replace("'", ""))
    df = df.fillna('')

    # Connect and load data
    mysql_connection = create_mysql_connection()
    load_data_to_mysql(df, mysql_connection)
    mysql_connection.close()

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