# -*- coding: utf-8 -*-
# kml -> document -> folder -> placemark (name, styleUrl, point(coordinates-long,lat,z))
# geolocator (lat, long)

from fastkml import kml
from geopy.geocoders import Nominatim
import lxml
from lxml import html
import pykml
import sys
from six.moves import urllib
from lxml import etree as ET
import pandas as pd
import googlemaps 
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt 
#from mpl_toolkits.basemap import Basemap
import json
import requests
import urllib.request as urlreq

#=========================1 INITIALIZING=========================================

writer = pd.ExcelWriter('pandas_geocodes.xlsx', engine='xlsxwriter')
with open('vego2.kml', 'rt', encoding="utf-8") as myfile: lava=myfile.read()
df = pd.DataFrame
print("========================================================")
print("API key not included   ")
print("========================================================")
#https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.961452&key=AIzaSyCqNZD1M7BEjN0LWb0bhtKLy7jwVEpEEi8

namelist = []
latlist = []
lonlist = []
coordslist = []
addlist = []

def filemake(df):
    print("saving....")
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print("saved")

#========================2 RAW DATA EXTRACTION======================================
    # Extract coordinates from KML file
    # Extract name of places (i.e. name of cafe, not the address)

lava = ET.fromstring(lava)

for element in lava.iter("coordinates"):        #Creates Latitude and Longitude List
     #print("%s - %s" % (element.tag, element.text))
     x = element.text
     x2 = x.split()
     x3 = x2[0]
     x4 = x3.split(",")
     xlon = x4[0]
     xlat = x4[1]
     xlatlng = '{0},{1}'
     xlatlng = xlatlng.format(xlat,xlon)
     latlist.append(xlat)
     lonlist.append(xlon)
     coordslist.append(xlatlng)

for element in lava.iter("name"):               #Extracts the Names of the Places
     #print("%s - %s" % (element.tag, element.text)) 
     n = element.text
     namelist.append(n)
namelist = namelist[2:]


#################################################################################
#=========================3 ADDRESS EXTRACTION===================================

def reverse(latlng):    
    apikey = 'insert your API here' #Get API from Google Developer
    cordz = latlng
    baseurl = 'https://maps.googleapis.com/maps/api/geocode/json?latlng={0}&key={1}'
    thelink = baseurl.format(cordz,apikey)
    data = json.loads(requests.get(thelink).text) #requests data based on coordinates
    return data # Returns address in raw json format

def loclist(coordslist): #processes a list of addresses 
    i = 0
    while i < len(coordslist):
        complete = reverse(coordslist[i])
        city = citydata(complete)
        print(city)
        i = i+1

def citydata(rawloc):
    city = rawloc['results'][0]['address_components'][3]['long_name']
    return city

def tester():
    latlng='40.714224 , -73.961452'
    latlng2 = '-33.8840884,151.2083165'
    q = reverse(latlng2)
    i = 0
    q2 = q['results'][1]['address_components'][3]['short_name']
    #print(q['results'][7])
    print(q['results'][1]['formatted_address'])
    
def masstest(coordslist):
    i = 0
    while i < len(coordslist):
        rawadd = reverse(coordslist[i])        
        rawadd2 = rawadd['results'][1]['address_components']
        x = 0
        addlist = 'Address: '
        while x < len(rawadd2):
            add = rawadd['results'][1]['address_components'][x]['short_name']
            x = x+1
            addlist = addlist + add
        print(addlist)
        i = i+1
        
def masstest2(coordslist):
    i = 0
    addlist = []
    while i <len(coordslist):
        rawadd = reverse(coordslist[i])        
        rawadd2 = rawadd['results'][1]['formatted_address']
    #    print(i,":",rawadd2,"\n")
        print(i+1,"out of ",len(coordslist))
        i = i+1
        addlist.append(rawadd2)
    print("finished address aggregation")
    return addlist
    


page = requests.get("http://dataquestio.github.io/web-scraping-pages/simple.html")
soup = BeautifulSoup(page.content, 'html.parser')
print(soup)

#----------------------------------------------------------------
#----------------------------------------------------------------
#=========================== Finalizing =========================


def Final():
    df = pd.DataFrame()
    df.insert(0, 'Name',namelist)
    df.insert(1, 'Latitude',latlist)
    df.insert(2, 'Longitude',lonlist)
    addlist = masstest2(coordslist)
    df.insert(3, 'Address', addlist)
    filemake(df)    

Final()
#----------------------------------------------------------------
#----------------------------------------------------------------
#----------------------------------------------------------------
#----------------------------------------------------------------
#================Useful Functions ===========
#----------------------------------------------------------------



def Inaccurate():
    i = 0    
    while i < namelen:
        cordz = latlist[i] + ", " + lonlist[i]
        loc = geolocator.reverse(cordz)
        print(i+1,": ",loc.address,"\n")
        i = i + 1


