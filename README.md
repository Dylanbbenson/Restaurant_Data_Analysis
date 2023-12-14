# Restaurant_Data_Analysis
This project is a data analysis of restaurant listings in any given U.S. city using the Yelp fusion api. This repo includes the following:

- **yelp_data_scrape.py**: python script that pulls restaurant data from Yelp's api for any given U.S. city, performs some data cleaning and transformation, then outputs it to a csv file.
  - syntax: python3 yelp_data_scrape.py --city <city> --state <state>
  - note: to use this script yourself, you'll need to obtain your own api key from the Yelp Developer tools.

- **load_restaurant_data.py**: python script that loads restaurants in csv file to a local mysql database. Also performs some etl by pulling and comparing existing data so as to not insert duplicate data.
  - syntax: python3 yelp_data_scrape.py --city <city> --state <state>

- **Restaurant_Master_ETL.py**: python script that executes the two previous scripts.
  - syntax: python3 yelp_data_scrape.py <city> <state>

- **Business_schema_ddl.sql**: sql script that creates and defines the schema to load this data to.
  
- **Restaurant_Data_Analysis.ipynb**: jupyter notebook that performs analysis on the extracted data.

- **Restaurant_Data_Analysis.pdf**: an example pdf report of visualized data created by the notebook. The city I used was my hometown Fargo, ND.

- **Restaurant_Data_Analysis.py**: a python script created as an alternative to the jupyter notebook.
	
- **dockerfile**: contains all the commands required to assemble the docker image for this project.
