# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 14:38:27 2019

@author: milailija
"""

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

# =============================================================================
# shapefile = 'D:\World_Seas_IHO_v3\World_Seas_IHO_v3.shp'
# oceans = gpd.read_file(shapefile)
# #oceans.plot()
# 
# p = figure(title="World Oceans")
# 
# #merged <- join datafile
# merged_json = json.loads(oceans.to_json())
# json_data = json.dumps(merged_json)
# 
# #Input GeoJSON source that contains features for plotting.
# # =============================================================================
# geosource = GeoJSONDataSource(geojson = json_data)
# 
# p.patches('xs','ys', source = geosource)
# =============================================================================

#show(p)

#save(obj=p, filename="test_map.html")
# 
app = Flask(__name__)

def read_data():
    shapefile = 'iho\iho.shp'
    oceans = gpd.read_file(shapefile)
    #MERGE DATA:
    #merged <- join datafile
    
    merged_json = json.loads(oceans.to_json())
    json_data = json.dumps(merged_json)
    print("Data read")
    return(json_data)

def make_plot(d):
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

if __name__ == '__main__':
    app.run(debug=False) #Set to false when deploying
