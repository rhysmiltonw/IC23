#Note: This is the same code as Top5Counties.ipynb. The only difference is that there is code making the plots.

#Step 1: Read the Given Crash CSV File and Population CSV using Pandas
import pandas as pd
from datetime import datetime
crash = pd.read_csv('Washington_Crash.csv')
zippop = pd.read_csv('zippop.csv')

#Step 2: Filter crash dataframe down into crashes that resulted in a fatality and occured after March 13th, 2020
crash['date'] = pd.to_datetime(crash['crash_dt'])
march_2020 = pd.to_datetime('03/13/2020') 
recent = crash[crash['date'] >= march_2020] #All dates after March 13th, 2020
recent_driver = recent[recent['ptype']==1] #Filets down to just drivers of the vehicle
recent_death = recent_driver[recent_driver['injury']==4] #Recent crashes that resulted in deaths

#Step 3: Using the recent_death dataframe, create a dictionary mapping the zip codes of the drivers to a count of crashes that occured there
zips = []
for i,row in recent_death.iterrows():
    try:
        row['dzip'] = int(row['dzip'])
    except:
        row['dzip'] = None
    zips.append(row['dzip'])

area = {}
for zip in zips:
    if zip in area.keys():
        area[zip] += 1
    else:
        area[zip] = 1

#Step 4: Using the area dictionary, sum all of the zip codes in the same county to get a dictionary that maps 
#the name of each county to the number of fatal crashes. While we're doing this, sum the population of each zipcode 
#in each county

population_county = {}
crashes_county = {}
for zipcode, count in area.items():
    for i,row in zippop.iterrows():
        if row['zip'] == zipcode:
            if row['county'] in crashes_county.keys():
                crashes_county[row['county']] += count
            else:
                crashes_county[row['county']] = count

for i,row in zippop.iterrows():
    if row['county'] in population_county.keys():         
        population_county[row['county']] += row['population']
    else:
        population_county[row['county']] = row['population']

print(crashes_county)

#Step 5: Calculate the Ratios
ratios = {}
for county, count in crashes_county.items():
    ratios[county] = count/population_county[county]

for county, ratio in ratios.items():
    county = county + ' County'
    if 0.00025986850653569296 <= ratio <=  0.00046438190768087673:
        print(county)

ratios = pd.DataFrame(ratios.items())
ratios['CTYNAME'] = ratios[0] + ' County'
ratios['ratio'] = ratios[1]
print(ratios)

countz = pd.DataFrame(crashes_county.items())
countz['CTYNAME'] = countz[0] + ' County'
countz['COUNT'] = countz[1]
print(countz)

#Create a Choropleth Map of county to ratio
fipsinfo = pd.read_csv('fipsinfo.csv')
new = fipsinfo[['FIPS','CTYNAME']]
combined = pd.merge(new,ratios,on='CTYNAME')
combined = pd.merge(countz,combined,on='CTYNAME')
combined = combined[['CTYNAME','FIPS','ratio','COUNT']]
combined['FIPS'] = combined['FIPS'].astype('string')
print(combined)


import plotly.express as px

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

fig = px.choropleth_mapbox(combined,geojson = counties,locations = 'FIPS',color = 'COUNT',hover_name = 'CTYNAME',
                           mapbox_style="carto-positron",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                           labels={'COUNT':'Count'}, title= 'Count of Fatal Car Crashes')

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

fig2 = px.choropleth_mapbox(combined,geojson = counties,locations = 'FIPS',color = 'ratio',hover_name = 'CTYNAME',
                           mapbox_style="carto-positron",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                           labels={'ratio':'Ratio'}, title= 'Ratio of Fatal Car Crashes (Count/Population)')

fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig2.show()

#https://plotly.com/python/mapbox-county-choropleth/
#https://plotly.github.io/plotly.py-docs/generated/plotly.express.choropleth_mapbox.html