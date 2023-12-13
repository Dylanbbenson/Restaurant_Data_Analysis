# Dockerfile for Restaurant Data Analysis
FROM python:3.9-slim-buster

WORKDIR /Restaurant_Data_Analysis

ADD yelp_data_scrape.py .
ADD Restaurant_Data_Analysis.ipynb .
ADD credentials.json .

RUN pip install yelpapi 
RUN pip install requests
RUN pip install pandas
#RUN pip install json
RUN pip install jupyter
RUN pip install datetime
RUN apt-get update -y
RUN pip install matplotlib
RUN pip install geopandas
RUN pip install seaborn
RUN pip install contextily
RUN apt-get install -y texlive-xetex
RUN mkdir /Restaurant_Data_Analysis/data
RUN mkdir /Restaurant_Data_Analysis/geodata

COPY yelp_data_scrape.py .
COPY Restaurant_Data_Analysis.ipynb .
COPY Restaurant_Data_Analysis.py .
COPY credentials.json .
COPY ./geodata/Fargo-Moorhead_Area-polygon.shp ./geodata

#CMD ["python", "./yelp_data_scrape.py"]
ENTRYPOINT ["python", "Restaurant_Data_Analysis.py"]
RUN jupyter nbconvert --to pdf Restaurant_Data_Analysis.ipynb --TemplateExporter.exclude_input=True