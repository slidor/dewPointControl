#!/usr/bin/python
# coding=utf-8
# dePointControl.py
#------------------

import os, sys, time
import Adafruit_DHT
import dweepy
import RPi.GPIO as GPIO

outdoorSensor = Adafruit_DHT.DHT22
outdoorSensorPin = 3

indoorSensor = Adafruit_DHT.DHT22
indoorSensorPin = 5

relaisPin = 7

GPIO.setmode(GPIO.BOARD)

GPIO.setup(relaisPin, GPIO.OUT)

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
  return cpuserial

def startVentilation():
    GPIO.output(relaisPin, GPIO.HIGH)

def stopVentilation():
    GPIO.output(relaisPin, GPIO.LOW)

def readSensorData():
    indoorHumidity, indoorTemperature = Adafruit_DHT.read.retry(indoorSensor, indoorSensorPin)
    oudoorHumidity, oudoorTemperature = Adafruit_DHT.read.retry(outdoorSensor, outdoorSensorPin)
    return(indoorHumidity, indoorTemperature, oudoorHumidity, oudoorTemperature)

def calculateAbsoluteHumidity(relHumidity, temperature):
    a = 7.5
    b = 237.3
    mw = 18.016
    R = 8314.3

    if (temperature < 0):
        a = 7.6
        b = 240.7

    TK = temperature + 273.15
    SDD = 6.1078 * 10**((a * temperature)/(b + temperature))
    DD = relHumidity/100 * SDD
    AF = 10**5 * mw/R * DD/TK

def ventilationMakesSense():
    result = false
    thingname = getserial() + "basementPi"

    indoorHumidity, indoorTemperature, oudoorHumidity, oudoorTemperature = readSensorData()
    absoluteIndoorHumidity = calculateAbsoluteHumidity(indoorHumidity, indoorTemperature)
    absoluteOutdoorHumidity = calculateAbsoluteHumidity(oudoorHumidity, oudoorTemperature)

    if (absoluteIndoorHumidity > absoluteOutdoorHumidity):
        result = true

    # Send sensor deta and results to dweet.io
    dweepy.dweet_for(thingname, {'indoorHumidity': indoorHumidity, 'indoorTemperature': indoorTemperature, 'absoluteIndoorHumidity': absoluteIndoorHumidity, 'oudoorHumidity': oudoorHumidity, 'oudoorTemperature': oudoorTemperature, 'absoluteOutdoorHumidity': absoluteOutdoorHumidity, 'ventilation': result})

    return result

if (ventilationMakesSense):
    startVentilation()
else:
    stopVentilation()
