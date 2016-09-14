#!/usr/bin/python
# coding=utf-8
# dePointControl.py
#------------------

import os, sys, time
import Adafruit_DHT
import dweepy
import RPi.GPIO as GPIO

# setup sensor type
outdoorSensor = Adafruit_DHT.DHT22
indoorSensor = Adafruit_DHT.DHT22

#define outdoor sensor GPIO pin
outdoorSensorPin = 3

#define indoor sensor GPIO pin
indoorSensorPin = 5

#define relais GPIO pin
relaisPin = 7


GPIO.setmode(GPIO.BOARD)
GPIO.setup(relaisPin, GPIO.OUT)

# define global variables
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
    print("startVentilation")
    GPIO.output(relaisPin, GPIO.HIGH)

def stopVentilation():
    print("stopVentilation")
    GPIO.output(relaisPin, GPIO.LOW)

def readSensorData():
    indoorHumidity, indoorTemperature = Adafruit_DHT.read.retry(indoorSensor, indoorSensorPin)
    print("indoorHumidity: " + indoorHumidity + "%")
    print("indoorTemperature: " + indoorTemperature + "°C")
    oudoorHumidity, oudoorTemperature = Adafruit_DHT.read.retry(outdoorSensor, outdoorSensorPin)
    print("oudoorHumidity: " + outdoorHumidity + "%")
    print("outdoorTemperature: " + outdoorTemperature + "°C")
    return(indoorHumidity, indoorTemperature, oudoorHumidity, oudoorTemperature)

def calculateDewPointTemperature(relHumidity, temperature):
	#relHumidity in percent
	return ((relHumidity / 100) ** (1 / 8.02)) * (109.8 + temperature) - 109.8

def ventilationMakesSense():
    result = false
    thingname = getserial() + "basementPi"

    indoorHumidity, indoorTemperature, oudoorHumidity, oudoorTemperature = readSensorData()
    indoorDewPoint = calculateDewPointTemperature(indoorHumidity, indoorTemperature)
    print("indoorDewPoint: " + indoorDewPoint + "°C")
    outdoorDewPoint = calculateDewPointTemperature(oudoorHumidity, oudoorTemperature)
    print("outdoorDewPoint: " + outdoorDewPoint + "°C")

	dewPointDiff = indoorDewPoint - outdoorDewPoint

    if (indoorTemperature > minIndoorTemp && (dewPointDiff >= dewPointLowerBorder || dewPointDiff <= dewPointUpperBorder):
    	result = true

    print("ventilationMakesSense: " + result)

    # Send sensor deta and results to dweet.io
    dweepy.dweet_for(thingname, {'indoorHumidity': indoorHumidity, 'indoorTemperature': indoorTemperature, 'indoorDewPoint': indoorDewPoint, 'oudoorHumidity': oudoorHumidity, 'oudoorTemperature': oudoorTemperature, 'outdoorDewPoint': outdoorDewPoint, 'ventilation': result})

    return result

if (ventilationMakesSense()):
    startVentilation()
else:
    stopVentilation()
