# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 14:38:27 2019

@author: milailija
"""
import numpy as np
import geopandas as gpd
import pandas as pd
import json
from flask import Flask, render_template
from bokeh.io import output_notebook, show, output_file, curdoc
from bokeh.plotting import figure, save
from bokeh.models import GeoJSONDataSource, Slider, HoverTool
from bokeh.palettes import brewer
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import CheckboxGroup
from bokeh.embed import components 

import requests
from bs4 import BeautifulSoup
import re
app = Flask(__name__)

def read_data():
    shapefile = 'iho/iho.shp'
    oceans = gpd.read_file(shapefile)
    #MERGE DATA:
    #merged <- join datafile
    
    merged_json = json.loads(oceans.to_json())
    json_data = json.dumps(merged_json)
    print("Data read")
    return(json_data)

def make_plot(d):
    risk = calculate_risk()
    TOOLTIPS=[("index", "$index"),("name", "$name")]
    p = figure(title="World Oceans", tools='pan, hover, wheel_zoom, reset')
    geosource = GeoJSONDataSource(geojson = d)
    p.patches('xs','ys', source = geosource)
    print("Plot made")
    return p

@app.route('/')
def homepage():
    print("?")
    #Read data
    d = read_data()
    p = make_plot(d)
    script, div = components(p)
    #print(script)
    return render_template('home.html', script=script, div=div)

from shapely.geometry import Polygon

def calculate_risk() :
    shapefile = 'iho/iho.shp'
    oceans = gpd.read_file(shapefile)
    #list of webpages of the weather stations
    weather_stations = ['https://www.infoclimat.fr/observations-meteo/temps-reel/kemi/02864.html','https://www.infoclimat.fr/observations-meteo/temps-reel/helsinki-malmi/02975.html','https://www.infoclimat.fr/observations-meteo/temps-reel/bagaskar/02984.html','https://www.infoclimat.fr/observations-meteo/temps-reel/market/02993.html','https://www.infoclimat.fr/observations-meteo/temps-reel/nyhamn/02980.html','https://www.infoclimat.fr/observations-meteo/temps-reel/oulu/02875.html','https://www.infoclimat.fr/observations-meteo/temps-reel/pori/02952.html']
    #list of zone coordinates
    station_coordinates = gpd.GeoSeries([Polygon([(66,24.58),(65.355,24.58),(65.355,25.37,64.63,25.37)]),Polygon([(64.63,23.6),(64.025,23.6),(64.025,23.15),(63.575,23.15)]),Polygon([(63.575,21.07),(63.24,21.07),(63.24,21.77,62.26,21.77)]),Polygon([(62.26,21.8),(50,21.8),(60.13,19),(60.13,19.935)]),Polygon([(59.97,19.935),(59.97,21.12),(60.52,21.12),(60.52,22.61)]),Polygon([(59.77,22.61),(59.77,23.485),(59.93,23.485),(59.93,24.535)]),Polygon([(60.25,24.535),(60.25,26.01),(60.37,26.01),(60.37,27)])])
    df1 = gpd.GeoDataFrame({'geometry': station_coordinates})
    results = [] #to put the zones coordinates
    item = 0
    res = {}
    ocean = gpd.read_file(shapefile)
    for i in weather_stations :
        r = requests.get(i)
        try :
            soup = BeautifulSoup(r.text,'html.parser')
            temp_max = soup.find_all(class_ = 'displayer')[0].get_text()
            regex = re.search("[[\s]*([\S]*])", temp_max)
            if regex!=None :
                temp_max = regex.group(1)
            else :
                temp_max = 0
            temp_min = soup.find_all(class_ = 'displayer')[1].get_text()
            regex = re.search("[\s]*([\S]*)", temp_min)
            regex = re.search("([0-9])",regex.group(1))
            if regex!=None :
                temp_min = regex.group(1)
            else :
                temp_min = 0
            temp_min = int(temp_min)
            try :
                rain = soup.find_all(class_ = 'displayer')[2].get_text()
            except :
                rain = 0
            if (temp_min > 10) and (temp_max > 15) :
                risk = 5.8*temp_max + rain*2
                if risk < 96 :
                    color = "green" #in more than 50% of cases, in those conditions there will be a bloom
                elif risk < 104 :
                    color = "yellow" #in more than 80% of cases, in those conditions there will be a bloom
                else :
                    color = "red" #in more than 95%...
            else :
                color="blue"
        except :
            color = "blue"
        res_intersection = gpd.overlay(df1, ocean, how='intersection')
        results.append(res_intersection)
        ocean=gpd.GeoDataFrame({'geometry': results})
        item = item + 1
        risk = 0
        color = "blue"

    return ocean

if __name__ == '__main__':
    app.run(debug=False) #Set to false when deploying
