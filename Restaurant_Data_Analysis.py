#!/usr/bin/env python
# coding: utf-8

# In[1]:


from yelpapi import YelpAPI
import requests
import pandas as pd
import json
import sys
import re
import warnings
import matplotlib.patches as mpatches
warnings.filterwarnings('ignore')
from datetime import date
from shapely.geometry import Point
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as colors
current_date = date.today().strftime('%Y-%m-%d')

city = 'Fargo'
state = 'nd'


# In[2]:


get_ipython().run_line_magic('run', 'yelp_data_scrape.py fargo nd')


# In[3]:


df = pd.read_csv("./data/"+city+"_Restaurants_"+current_date+".csv")
df = df[['name', 'review_count', 'rating', 'transactions', 'price', 'phone', 'display_phone', 'display_address', 'latitude', 'longitude', 'foodtype']]
df.head()


# In[17]:


#Plot a map of Restaurants
geometry = [Point(xy) for xy in zip(df['longitude'],df['latitude'])]

wardlink = "./geodata/Fargo-Moorhead_Area-polygon.shp"

ward = gpd.read_file(wardlink, bbox=None, mask=None, rows=None)
geo_df = gpd.GeoDataFrame(geometry = geometry)

ward.crs = {'init':"epsg:4326"}
geo_df.crs = {'init':"epsg:4326"}

ax = ward.plot(alpha=0.35, color='#ffffff', zorder=1)
ax = geo_df.plot(ax = ax, markersize = 20, color = 'red',marker = '*',label = city, zorder=3)
ctx.add_basemap(ax, crs=geo_df.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
print("Total Number of Restaurants in "+city+": "+str(len(df)))
plt.show()


# In[5]:


ratings = df.sort_values(['rating', 'review_count'], ascending=[False, False])
ratings = ratings[ratings['review_count'] != 0]
print("Top Ten highest rated restaurants in "+city+":")
ratings.head(10)


# In[6]:


print("Top Ten lowest rated restaurants in "+city+":")
ratings.tail(10)


# In[7]:


transactions_df = df["transactions"].value_counts()
transactions_df.plot.pie(figsize=(15, 10), autopct='%1.1f%%', colors=['red', 'green', 'blue', 'purple', 'orange', 'pink', 'yellow'])
plt.title("Transaction Types for Restaurants in "+city, fontdict={'size': 15, 'weight': 'bold'})
plt.ylabel("")
plt.show()


# In[8]:


#convert food types
def map_foodtypes(foodtype):
    if foodtype == "restaurants":
        return 'miscellaneous'
    elif foodtype == "tacos":
        return 'mexican'
    elif foodtype == "burgers" or foodtype == "chicken_wings" or foodtype == "tradamerican" or foodtype == "newamerican":
        return 'american'
    if foodtype == "sandwiches" or foodtype == "soup":
        return 'soup_sandwich'
    elif foodtype == "breakfast_brunch":
        return 'breakfast'
    if foodtype == "sportsbars" or foodtype == "cocktailbars" or foodtype == "wine_bars":
        return 'bars'
    elif foodtype == "ramen":
        return 'noodles'    
    elif foodtype == "irish_pubs" or foodtype == "gastropubs":
        return 'pubs'  
    elif foodtype == "bagels":
        return 'bakeries'
    elif foodtype == "cupcakes" or foodtype == "donuts":
        return 'desserts' 
    elif foodtype == "asianfusion":
        return 'asian' 
    elif foodtype == "egyptian" or foodtype == "lebanese":
        return 'mideastern'
    elif foodtype == "cheesesteaks":
        return 'steak'  
    elif foodtype == "danceclubs" or foodtype == "nightclubs":
        return 'nightlife'     
    else:
        return foodtype

# apply the function to create the new column
df["foodtype"] = df["foodtype"].apply(map_foodtypes)


# In[9]:


#create pie chart of food types
foodtype_count = df["foodtype"].value_counts()

# create new category that groups builders making up <2% of total
total = foodtype_count.sum()
threshold = 0.015

foodtype_percent = foodtype_count/foodtype_count.sum()
other_percent = foodtype_percent[foodtype_percent < threshold].sum()
foodtype_percent = foodtype_percent[foodtype_percent >= threshold]
foodtype_percent["other (<1.5% share)"] = other_percent

foodtype_percent.plot.pie(figsize=(15, 10), autopct='%1.1f%%', colors=['red', 'green', 'blue', 'purple', 'orange', 'pink', 'yellow'])
plt.title("Restaurants Food Types in "+city, fontdict={'size': 15, 'weight': 'bold'})
plt.ylabel("")
plt.show()


# In[10]:


colormap = {
'american': 'red',
'italian': 'blue',
'chinese': 'green',
'mexican': 'yellow',
'thai': 'orange',
'indian': 'purple',
'greek': 'brown',
'pizza': 'gray',
'bars': 'teal',
'foodtrucks': 'pink',
'icecream': 'violet',
'breakfast': 'beige',
'coffee': 'turquoise',
'soup_sandwich': 'gold',
'hotdogs': 'silver'
}

geo_df['color'] = df['foodtype'].map(colormap)


legend_patches = [mpatches.Patch(color=color, label=food_type) for food_type, color in colormap.items()]

ax = ward.plot(alpha=0.35, color='#ffffff', zorder=1)
ax = geo_df.plot(ax=ax, markersize=20, column='color', marker='*', label=city, zorder=3)
ctx.add_basemap(ax, crs=geo_df.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
plt.legend(handles=legend_patches, loc="upper left", prop={'size': 6})
plt.show()


# In[11]:


#convert price to word format
def map_price(price):
    if price == "$":
        return 'Low'
    elif price == "$$":
        return 'Medium'
    elif price == "$$$":
        return 'High'
    elif price == "$$$$":
        return 'Very High'
    elif price == "None":
        return 'Unlisted'
    else:
        return price

# apply the function to create the new column
df["price_val"] = df["price"].apply(map_price)
price_count = df["price_val"].value_counts()
price_count


# In[12]:


price_count.plot.pie(figsize=(15, 10), autopct='%1.1f%%', colors=['red', 'green', 'blue', 'purple', 'orange', 'pink', 'yellow'])
plt.title("Restaurants Prices in "+city, fontdict={'size': 15, 'weight': 'bold'})
plt.ylabel("")
print("Note: This chart doesn't include restaurants where the price wasn't listed")
plt.show()


# In[13]:


# Group by foodtype and calculate the mean rating
average_rating = df.groupby('foodtype')['rating'].mean()
average_rating = pd.DataFrame(average_rating)
average_rating = pd.merge(average_rating, df.groupby('foodtype')['review_count'].sum(), on='foodtype')
average_rating = average_rating[average_rating['review_count'] != 0]
average_rating = average_rating.sort_values(['rating'], ascending=[False])

restaurant_count = df["foodtype"].value_counts()
restaurant_count = pd.DataFrame(restaurant_count)
restaurant_count

average_rating = pd.merge(average_rating, restaurant_count, left_index=True, right_index=True)
average_rating = average_rating.rename(columns={'foodtype': 'restaurant_count'}) 
average_rating


# In[14]:


sns.set(rc={"figure.figsize":(20, 5)})
rating_barplot = sns.barplot(x = average_rating.index, y = 'rating', data = average_rating)
plt.xlabel('Restaurant Food Type')
plt.ylabel('Average Rating')
rating_barplot.set_xticklabels(rating_barplot.get_xticklabels(), rotation=45, horizontalalignment='right')
plt.title('Average Rating per Restaurant Food Type Across '+ city, fontdict={'size': 20, 'weight': 'bold'})
plt.show()


# In[15]:


average_rating = average_rating.sort_values(['restaurant_count'], ascending=[False])
sns.set(rc={"figure.figsize":(20, 5)})
rating_barplot = sns.barplot(x = average_rating.index, y = 'restaurant_count', data = average_rating)
plt.xlabel('Restaurant Food Type')
plt.ylabel('Number of Locations')
rating_barplot.set_xticklabels(rating_barplot.get_xticklabels(), rotation=45, horizontalalignment='right')
plt.title('Restaurant Count per Food Type Across '+ city, fontdict={'size': 20, 'weight': 'bold'})
plt.show()


# In[16]:


average_rating = average_rating.sort_values(['review_count'], ascending=[False])
sns.set(rc={"figure.figsize":(20, 5)})
rating_barplot = sns.barplot(x = average_rating.index, y = 'review_count', data = average_rating)
plt.xlabel('Restaurant Food Type')
plt.ylabel('Number of Reviews')
rating_barplot.set_xticklabels(rating_barplot.get_xticklabels(), rotation=45, horizontalalignment='right')
plt.title('Total Review Count per Food Type Across '+ city, fontdict={'size': 20, 'weight': 'bold'})
plt.show()


# In[18]:


df


# In[24]:


df = df.sort_values(['price'], ascending=[False])
print("Top Ten most expensive restaurants in "+city+":")
df.head(10)


# In[ ]:





# In[ ]:




