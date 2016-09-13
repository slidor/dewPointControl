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

dewPointLowerBorder = 2
dewPointUpperBorder = 9
minIndoorTemp = 10

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

def calculateDewPointTemperature(relHumidity, temperature):
	#relHumidity in percent
	return ((relHumidity / 100) ** (1 / 8.02)) * (109.8 + temperature) - 109.8 

def ventilationMakesSense():
    result = false
    thingname = getserial() + "basementPi"

    indoorHumidity, indoorTemperature, oudoorHumidity, oudoorTemperature = readSensorData()
    indoorDewPoint = calculateDewPointTemperature(indoorHumidity, indoorTemperature)
    outdoorDewPoint = calculateDewPointTemperature(oudoorHumidity, oudoorTemperature)
	
	dewPointDiff = indoorDewPoint - outdoorDewPoint
	
    if (indoorTemperature > minIndoorTemp && (dewPointDiff >= dewPointLowerBorder || dewPointDiff <= dewPointUpperBorder):
    	return true

    # Send sensor deta and results to dweet.io
    dweepy.dweet_for(thingname, {'indoorHumidity': indoorHumidity, 'indoorTemperature': indoorTemperature, 'indoorDewPoint': indoorDewPoint, 'oudoorHumidity': oudoorHumidity, 'oudoorTemperature': oudoorTemperature, 'outdoorDewPoint': outdoorDewPoint, 'ventilation': result})

    return result

if (ventilationMakesSense):
    startVentilation()
else:
    stopVentilation()
