#!/usr/bin/env python
# coding: utf-8
import RPi.GPIO as GPIO
import time

class ColorSensor(object):

    def __init__(self):
        self.s0 = 14 #4
        self.s1 = 15 #17
        self.s2 = 8  #27
        self.s3 = 7  #22
        self.out = 1 #6

        self.NUM_CYCLES = 5 # 값이 높을수록 속도 떨어지지만 정확도 올라감 
        GPIO.setwarnings(False)
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.out,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.s2,GPIO.OUT)
        GPIO.setup(self.s3,GPIO.OUT)
        GPIO.setup(self.s1,GPIO.OUT)
        GPIO.setup(self.s0,GPIO.OUT)

        GPIO.output(self.s0,GPIO.LOW)
        GPIO.output(self.s1,GPIO.HIGH)
    
    def check(self): #(R,G,B)
        GPIO.output(self.s2,GPIO.LOW)
        GPIO.output(self.s3,GPIO.LOW)
        start = time.time()
        for _ in range(self.NUM_CYCLES):
            GPIO.wait_for_edge(self.out, GPIO.FALLING)
        duration = time.time() - start 
        red  = self.NUM_CYCLES / duration
           
        GPIO.output(self.s2,GPIO.LOW)
        GPIO.output(self.s3,GPIO.HIGH)
        start = time.time()
        for _ in range(self.NUM_CYCLES):
            GPIO.wait_for_edge(self.out, GPIO.FALLING)
        duration = time.time() - start
        blue = self.NUM_CYCLES / duration
    
        GPIO.output(self.s2,GPIO.HIGH)
        GPIO.output(self.s3,GPIO.HIGH)
        start = time.time()
        for _ in range(self.NUM_CYCLES):
            GPIO.wait_for_edge(self.out, GPIO.FALLING)
        duration = time.time() - start
        green = self.NUM_CYCLES / duration
        
        return (red,green,blue)
    
    def isGreen(self,rgb):
        red,green,blue = rgb
        total = sum(rgb)
        red /= total
        green /= total
        blue /= total
        
        return (green + blue > 0.65 and rgb[2] / rgb[1] < 1.2)
        
     
    def isRed(self,rgb):
        red,green,blue = rgb
        total = sum(rgb)
        red /= total
        green /= total
        blue /= total
        
        return (red > 0.4 and green < 0.3 and blue < 0.3)
        
    
    def isBlue(self,rgb):
        red,green,blue = rgb
        total = sum(rgb)
        red /= total
        green /= total
        blue /= total
        
        return (blue > 0.5 and red < 0.3 and green < 0.3)        

    
    def isYellow(self,rgb):
        red,green,blue = rgb
        total = sum(rgb)
        red /= total
        green /= total
        blue /= total
        
        return (red + green > 0.7 and total > 1000)
        
    def isWhite(self,rgb):
        return sum(rgb) >6000 

    def isBlack(self,rgb):
        return sum(rgb) < 1200
        
    def stop(self):
        GPIO.cleanup()
