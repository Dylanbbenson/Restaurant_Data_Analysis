import pandas as pd
import mysql.connector
from datetime import date
import sys
import argparse
from decouple import config
from dotenv import load_dotenv
import warnings
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import NoSuchTableError

load_dotenv(dotenv_path='config.env')

current_date = date.today().strftime('%Y-%m-%d')

def get_user_input():
    city = input("Enter the City: ")
    state = input("Enter the State: ")
    query = input("Enter your search query: ")
    return city, state, query

def main(city, state, query):
    
    city = city.replace(" ", "-")
    city = city.capitalize()
    city_state = city + ", " + state
    
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
            search_query = "SELECT name, address FROM Business."+query
            existing_data = pd.read_sql(search_query, connection)
            return existing_data

        # Load data into table, only if the record doesn't exist
        def load_data_to_mysql(data, existing_data, connection):
            cursor = connection.cursor()

            for index, row in data.iterrows():
                # Check if the record already exists
                if (row['name'], row['address']) not in zip(existing_data['name'], existing_data['address']):
                    columns = ", ".join(data.columns)
                    values = ", ".join(["%s" for _ in range(len(data.columns))])
                    insert_query = f"INSERT INTO Business."+query+"({columns}) VALUES ({values})"
                    cursor.execute(insert_query, tuple(row))

            connection.commit()
            cursor.close()

        # Perform some data transformation
        df = pd.read_csv(f"../data/{city}_{query}_{current_date}.csv")
        df = df[['name', 'display_address', 'review_count', 'rating', 'transactions', 'price', 'phone', 'display_phone', 'latitude', 'longitude', 'foodtype', 'city', 'state', 'country']]
        df = df.rename(columns={'display_address': 'address'}) 
        df['address'] = df['address'].apply(lambda x: x.replace("[", "").replace("]", "").replace("'", ""))
        df = df.fillna('')
        
        # Check if the table exists
        metadata = MetaData(bind=engine)
        table_name = query
        try:
            query_table = Table(table_name, metadata, autoload=True)
        except NoSuchTableError:
            print(f"The table '{table_name}' does not exist. Creating the table...")

        # Define the table structure based on the DataFrame
        df.to_sql(table_name, engine, index=False, if_exists='replace')

        print(f"The table '{table_name}' has been created.")

        # Connect and load data
        mysql_connection = create_mysql_connection()
        existing_data = load_existing_data(mysql_connection)
        load_data_to_mysql(df, existing_data, mysql_connection)
        mysql_connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", help="City name")
    parser.add_argument("--state", help="State abbreviation")
    parser.add_argument("--query", help="Search query")

    args = parser.parse_args()

    if args.city and args.state and args.query:
        main(args.city, args.state, args.query)
    else:
        city, state, query = get_user_input()
        main(city, state, query)