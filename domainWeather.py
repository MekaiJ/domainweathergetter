#! /usr/bin/env python3
# author: Mekai Johnson

from json import loads  # steps 3, 4
from requests import get  # steps 3, 4
from socket import gethostbyname  # step 1
from subprocess import getstatusoutput  # step 2
from sys import argv  # command line arguments
import matplotlib.pyplot as plt #for temp plotting function
import numpy as np #for temp plotting function

# Takes an array of temps
# and plots them.
def plot_temps(temps):
    xs = [x for x in range(len(temps))]
    plt.plot(xs, temps, label="Hourly tempatures")

    #Label the x and y
    plt.xlabel("Hour")
    plt.ylabel("Temperature F.")
    #Make sure we show the legend.
    plt.legend()
    #Show the plot
    plt.show()


def main():

    # STEP 1: Look up IP address of specified domain
    domainIP = gethostbyname(argv[1])

    # STEP 2: use whois to get the physical address of the host
    physAddr = getstatusoutput(f"whois {domainIP}")
    temp = physAddr[1].split("\n")
    address = ""
    city = ""
    state = ""
    postalcode = ""
    for element in temp:
        if element.startswith("Address:"):
            address = element.strip("Address:").strip()
        if element.startswith("City"):
            city = element.strip("City:").strip()
        if element.startswith("StateProv:"):
            state = element.strip("StateProv:").strip()
        if element.startswith("PostalCode:"):
            postalcode = element.strip("PostalCode:").strip()
    location = {"address": address, "city": city, "state": state, "zip": postalcode}

    # STEP 3: Convert the physical address to latitude/longitude
    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
    params = {
        "address": f"{location['address']}, {location['city']}, {location['state']}, {location['zip']}",
        "benchmark": "4",
        "format": "json"
    }
    response = get(url, params=params)
    geoJson = loads(response.text)
    x = geoJson['result']['addressMatches'][0]['coordinates']['x']
    y = geoJson['result']['addressMatches'][0]['coordinates']['y']
    
    # STEP 4: send the latitude and longitude to the weather api 
    weather_s = "https://api.weather.gov/points/"
    weatherResponse = get(weather_s + f"{y},{x}")
    js = loads(weatherResponse.text)
    forecast_URL = js['properties']['forecastHourly']
    final_response = get(forecast_URL)

    # Step 5: Plot the temperatures recieved from the weather API
    fsjs = loads(final_response.text)
    temperatures = []
    for temp in range(155):
        temperatures.append(fsjs['properties']['periods'][temp]['temperature'])
        
    plot_temps(temperatures)




if __name__ == "__main__":
    main()
