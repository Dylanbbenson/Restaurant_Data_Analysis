import pandas as pd
import mysql.connector
from datetime import date
import sys
import argparse
from decouple import config
from dotenv import load_dotenv
import warnings

load_dotenv(dotenv_path='config.env')

current_date = date.today().strftime('%Y-%m-%d')

def get_user_input():
    city = input("Enter the City: ")
    state = input("Enter the State: ")
    return city, state

def main(city, state):
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)

        # Establish DB connection
        def create_mysql_connection():
            connection = mysql.connector.connect(
                host=config('DB_HOST'),
                user=config('DB_USER'),
                password=config('DB_PASSWORD'),
                database=config('DB_NAME')
            )
            return connection

        # Load existing data from the database
        def load_existing_data(connection):
            query = "SELECT name, address FROM Business.restaurants"
            existing_data = pd.read_sql(query, connection)
            return existing_data

        # Load data into table, only if the restaurant doesn't exist
        def load_data_to_mysql(data, existing_data, connection):
            cursor = connection.cursor()

            for index, row in data.iterrows():
                # Check if the restaurant already exists
                if (row['name'], row['address']) not in zip(existing_data['name'], existing_data['address']):
                    columns = ", ".join(data.columns)
                    values = ", ".join(["%s" for _ in range(len(data.columns))])
                    insert_query = f"INSERT INTO Business.restaurants ({columns}) VALUES ({values})"
                    cursor.execute(insert_query, tuple(row))

            connection.commit()
            cursor.close()

        # Perform some data transformation
        df = pd.read_csv(f"./data/{city}_Restaurants_{current_date}.csv")
        df = df[['name', 'display_address', 'review_count', 'rating', 'transactions', 'price', 'phone', 'display_phone', 'latitude', 'longitude', 'foodtype', 'city', 'state', 'country']]
        df = df.rename(columns={'display_address': 'address'}) 
        df['address'] = df['address'].apply(lambda x: x.replace("[", "").replace("]", "").replace("'", ""))
        df = df.fillna('')

        # Connect and load data
        mysql_connection = create_mysql_connection()
        existing_data = load_existing_data(mysql_connection)
        load_data_to_mysql(df, existing_data, mysql_connection)
        mysql_connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", help="City name")
    parser.add_argument("--state", help="State abbreviation")

    args = parser.parse_args()

    if args.city and args.state:
        main(args.city, args.state)
    else:
        city, state = get_user_input()
        main(city, state)