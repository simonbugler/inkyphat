#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import urllib
from PIL import Image, ImageFont
import subprocess
import inkyphat
try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

# Functions

def shorten(text, length):
    # Process text to be shorter than [length] chars
    str(text)
    if len(text) > length:    
        newtext = ""
        for word in text.split():
            newtext += word[0:4]
            newtext += "."
        return(newtext)
    else:
        return(text)

def degrees_to_cardinal(degrees):
    try:
        cardinal = ["North", "NNE", "NE", "ENE", "East", "ESE", "SE", "SSE",
                "South", "SSW", "SW", "WSW", "West", "WNW", "NW", "NNW"]
        ix = int((degrees + 11.25)/22.5)
        return cardinal[ix % 16]
    except:
        return "Err :("

def get_ip_address(interface):
    try:
        s = subprocess.check_output(["ip","addr","show",interface])
        return s.split('\n')[2].strip().split(' ')[1].split('/')[0]
    except:
        return "Could not find IP address :("

def get_up_stats():
    # Returns a tuple (uptime, 5 min load average)
    try:
        s = subprocess.check_output(["uptime"])
        load_split = s.split('load average: ')
        load_five = float(load_split[1].split(',')[1])
        up = load_split[0]
        up_pos = up.rfind(',',0,len(up)-4)
        up = up[:up_pos].split('up ')[1]
        return ( "UP", up ," L", int(load_five*100),"%" )        
    except:
        return ( '' , 0 )

def get_process_count():
    # Returns the number of processes
    try:
        s = subprocess.check_output(["ps","-e"])
        return len(s.split('\n'))        
    except:
        return 0

def get_temperature():
    try:
        s = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_temp"])
        return float(s.split('=')[1][:-3])
    except:
        return 0

def get_ram():
    # Returns a tuple (total ram, available ram) in megabytes
    try:
        s = subprocess.check_output(["free","-m"])
        lines = s.split('\n')
        return ( int(lines[1].split()[1]), int(lines[2].split()[3]) )
    except:
        return 0


# Python 2 vs 3 breaking changes
def encode(qs):
    val = ""
    try:
        val = urllib.urlencode(qs).replace("+","%20")
    except:
        val = urllib.parse.urlencode(qs).replace("+", "%20")
    return val

def get_weather(address):
    # https://developer.yahoo.com/weather/documentation.html
    base = "https://query.yahooapis.com/v1/public/yql?"
    query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text=\""+address+"\")"
    qs={"q": query, "format": "json", "env": "store://datatables.org/alltableswithkeys"}

    uri = base + encode(qs)                                        

    res = requests.get(uri)
    if(res.status_code==200):
        json_data = json.loads(res.text)
        return json_data

    return {}

print ("Functions loaded")

# Processing

datetime = time.strftime("%d/%m %H:%M")

CITY = "Swanage"
COUNTRYCODE = "GB"
WARNING_TEMP = 25.0

location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)

weather = get_weather(location_string)

pressure = 0
pressurestatestr = ""
winddir = 0
windchill = 0
windspeed = 0.0
temperature = 0
weathertext0 = ""
weathertext1 = ""
weathertext2 = ""

if "channel" in weather["query"]["results"]:
    results = weather["query"]["results"]["channel"]
    pressure = results["atmosphere"]["pressure"]
    pressurestate = results["atmosphere"]["rising"]
    winddir = degrees_to_cardinal(int(results["wind"]["direction"]))
    windchill = (int(results["wind"]["chill"]) - 32) * .5556
    windspeed = results["wind"]["speed"]
    temperature = (int(results["item"]["forecast"][0]["high"]) - 32) * .5556
    weathertext0 = results["item"]["forecast"][0]["text"]
    weathertext1 = results["item"]["forecast"][1]["text"]
    weathertext2 = results["item"]["forecast"][2]["text"]


    if pressurestate == "0":
        pressurestatestr = "Steady"
    elif pressurestate == "1":
        pressurestatestr = "Rising"
    elif pressurestate == "2":
        pressurestatestr = "Falling"


else:
    print("Warning, no weather information found!")

print ("Processing done")
# Display

font = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", 10)
fontsm = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", 6)
fontlg = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", 16)

inkyphat.set_rotation(180)
inkyphat.set_colour('red')
inkyphat.set_border(inkyphat.BLACK)

# Load the backdrop image
inkyphat.set_image("/home/pi/Pimoroni/inkyphat/examples/resources/inkyphat-bg3.png")

# Print text
# Top Left
inkyphat.text((6, 7), datetime, inkyphat.BLACK, font=font)
# Left
inkyphat.text((6, 21), ''.join(map(str, get_up_stats())), inkyphat.BLACK, font=font)
inkyphat.text((6, 31), "T"+str(get_temperature())+"C PR:"+str(get_process_count()), inkyphat.BLACK, font=font)
inkyphat.text((6, 41), 'mb- '.join(map(str, get_ram()))+'mb+', inkyphat.BLACK, font=font)
# Bottom Row
inkyphat.text((6, 87), get_ip_address("wlan0"), inkyphat.WHITE, font=font)
# Right
inkyphat.text((108, 7), u"{:.1f}c".format(temperature)  + " {}mb ".format(pressure) , inkyphat.WHITE if temperature < WARNING_TEMP else inkyphat.RED, font=font)
inkyphat.text((108, 17), pressurestatestr, inkyphat.WHITE, font=font)
inkyphat.text((108, 27), str(windspeed) + "mph " + str(winddir), inkyphat.WHITE, font=font)
inkyphat.text((108, 37), "feels " + u"{:.1f}c ".format(windchill), inkyphat.WHITE, font=font)

inkyphat.line((108, 47, 200, 47), 2) # Red line

inkyphat.text((108, 49), shorten(weathertext0, 14), inkyphat.WHITE, font=font)
inkyphat.text((108, 59), shorten(weathertext1, 14), inkyphat.WHITE, font=font)
inkyphat.text((108, 69), shorten(weathertext2, 14), inkyphat.WHITE, font=font)

inkyphat.show()
print ("Display updated")
