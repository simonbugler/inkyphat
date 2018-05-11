#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import signal
import buttonshim
import inkyphat
import os
from PIL import Image, ImageFont
import inkyphat
import time
import urllib2
import textwrap
import twitter 
#pip install python-twitter


def flash_led(interval, times, r, g, b):
    for i in range(times):
        buttonshim.set_pixel(r, g, b)
        time.sleep(interval)
        buttonshim.set_pixel(0, 0, 0)
        time.sleep(interval)

def buttonflash():
    flash_led(0.025, 3, 255, 255, 255) 

def runprocess(file):
    try:
        # run process
        process = subprocess.Popen(file, shell=True)
        # flash green led to show its working
        flash_led(0.5, 14, 0, 255, 0)
        # wait for the process to complete
        process.communicate()
        # flash blue led to show its finshed
        flash_led(0.05, 5, 0, 0, 255)   
    except Exception as error:
        printtoscreen("Error", error)

def printtoscreen(title="", content="Error"):
    
    # draw a rectangle of white to clear previous screen if using a loop - as in twitter output
    inkyphat.rectangle([(0, 0), (212, 104)], fill=inkyphat.WHITE, outline=None)

    if len(content) < 200:
        fontsize = 10
        charwidth = 29
        lineheight = 9
    else:
        fontsize = 6
        charwidth = 41
        lineheight = 6

    font = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", fontsize)
    fontmedium = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", 10)
    inkyphat.set_rotation(180)
    inkyphat.set_border(inkyphat.BLACK)

    # title
    inkyphat.rectangle([(1, 1), (210, 13)], fill=inkyphat.BLACK, outline=None)
    inkyphat.text((2, 3), title, inkyphat.WHITE, font=fontmedium)

    # main body of text - line wrapped 
    y = 17
    for line in textwrap.wrap(content, charwidth):
         inkyphat.text((2, y), line, inkyphat.BLACK, font=font)
         y = y + lineheight

    flash_led(0.5, 3, 0, 255, 0)

    inkyphat.show()

    flash_led(0.05, 5, 0, 0, 255)

def wait_for_internet_connection():
    while True:
        try:
            response = urllib2.urlopen('http://www.google.com',timeout=1)
            runprocess("/home/pi/Pimoroni/inkyphat/examples/info.py")
            return
        except urllib2.URLError:
            pass
            printtoscreen("Message","Waitng for internet connection")


# Button presses/release

# Button A - Runs a QR code example
@buttonshim.on_release(buttonshim.BUTTON_A)
def button_a(button, pressed):
    buttonflash()
    runprocess("/home/pi/Pimoroni/inkyphat/examples/qr.py 'http://www.electromaker.io'")

# Button B - displays Twitter feed example - you need to sign up for a twitter app api and fill in the details below 
@buttonshim.on_release(buttonshim.BUTTON_B)
def button_b(button, pressed):
    buttonflash()
    api = twitter.Api(consumer_key='-',
    consumer_secret='-',
    access_token_key='-',
    access_token_secret='-')

    search = api.GetUserTimeline(screen_name="ElectromakerIO", count=3)
    for tweet in search:
        tweettext = tweet.text
        printtoscreen("Twitter",tweettext)


# Button C - runs the weather - IP - time/date and system info splash screen - updates every 10 minutes
@buttonshim.on_release(buttonshim.BUTTON_C)
def button_c(button, pressed):
    buttonflash()
    # Refresh it every 600 seconds to stop loop must restart service process - hold button A
    starttime=time.time()
    while True:
        runprocess("/home/pi/Pimoroni/inkyphat/examples/info.py")
        time.sleep(600.0 - ((time.time() - starttime) % 600.0))

# Button D - Runs a image display example
@buttonshim.on_release(buttonshim.BUTTON_D)
def button_d(button, pressed):
    buttonflash()
    inkyphat.set_rotation(180)
    inkyphat.set_image(Image.open("/home/pi/Pimoroni/inkyphat/examples/resources/oct2.png"))
    inkyphat.show()

# Button E - Runs the name badge example
@buttonshim.on_release(buttonshim.BUTTON_E)
def button_e(button, pressed):
    buttonflash()
    runprocess('/home/pi/Pimoroni/inkyphat/examples/hello.py "SIMON BUGLER"')


# BUTTTON HOLDS

# Restarts Service    
@buttonshim.on_hold(buttonshim.BUTTON_A)
def button_a_hold(button):
    flash_led(0.05, 3, 255, 0, 0)
    os.system('sudo svc -k /etc/service/rainbow/')

# Reboots Pi
@buttonshim.on_hold(buttonshim.BUTTON_B)
def button_b_hold(button):
    flash_led(0.05, 3, 255, 0, 0)
    os.system('sudo reboot')

# Shutdown Pi
@buttonshim.on_hold(buttonshim.BUTTON_C)
def button_c_hold(button):
    flash_led(0.05, 3, 255, 0, 0)
    os.system('sudo shutdown -h now')


# Run initial python script info.py when internet connection established
wait_for_internet_connection()

signal.pause()