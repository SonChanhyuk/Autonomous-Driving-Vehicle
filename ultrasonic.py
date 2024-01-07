#!/usr/bin/env python
# coding: utf-8

import RPi.GPIO as GPIO
import time
import car

class Ultrasonic(object):

    def __init__(self):
        self.trig = 23
        self.echo = 24
  
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig,GPIO.OUT)
        GPIO.setup(self.echo,GPIO.IN)

        GPIO.output(self.trig, GPIO.LOW)
     
    def check(self):
        GPIO.output(self.trig,GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trig,GPIO.LOW)

        while not (GPIO.input(self.echo)):
            start = time.time()
        while (GPIO.input(self.echo)):
            stop = time.time() 

        return ((stop - start)* 34300 / 2)

