# Dockerfile for Restaurant Data Analysis
FROM python:3.9-slim-buster

WORKDIR /Restaurant_Data_Analysis

Add requirements.txt .
ADD yelp_data_scrape.py .
ADD Restaurant_Data_Analysis.ipynb .
ADD credentials.json .

COPY yelp_data_scrape.py .
COPY Restaurant_Data_Analysis.ipynb .
COPY Restaurant_Data_Analysis.py .
COPY credentials.json .
COPY ./geodata/Fargo-Moorhead_Area-polygon.shp ./geodata

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install -y texlive-xetex
RUN mkdir /Restaurant_Data_Analysis/data
RUN mkdir /Restaurant_Data_Analysis/geodata

#replace the <city> and <state_abbv> parameters with the city you want
CMD ["python", "your_script.py", "--city", "<city>", "--state", "<state_abbv>"]
RUN jupyter nbconvert --to pdf Restaurant_Data_Analysis.ipynb --TemplateExporter.exclude_input=True