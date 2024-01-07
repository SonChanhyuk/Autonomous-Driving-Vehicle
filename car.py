#!/usr/bin/env python
# coding: utf-8
import smbus
import RPi.GPIO as GPIO
import time

class Car(object):

    def __init__(self):
        self.addr = 0x16
        self.reg = 0x01
        self.buzz_BCM = 12
        self.device = smbus.SMBus(1)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzz_BCM, GPIO.OUT)
        
    def buzzer_init(self):
        self.buzz = GPIO.PWM(self.buzz_BCM,350)

    def write_array(self, reg, data):
        try:
            self.device.write_i2c_block_data(self.addr, reg, data)
        except:
            print ('write_array error')

    def run(self, left_speed, right_speed):
        data = [1, int(left_speed), 1, int(right_speed)]
        self.write_array(self.reg,data)


    def back(self, left_speed, right_speed):
        data = [0, int(left_speed), 0, int(right_speed)]
        self.write_array(self.reg,data)

    def turn_right(self, speed):
        data = [1,int(speed),0,int(speed)]
        self.write_array(self.reg,data)

    def turn_left(self, speed):
        data = [0,int(speed),1,int(speed)]
        self.write_array(self.reg,data)

    def stop(self):
        reg = 0x02
        self.device.write_byte_data(self.addr,reg,0x00)

    def servo(self,sensor,angle):
        reg = 0x03
        if (angle < 0):
            angle = 0
        elif (angle > 180):
            angle = 180
        data = [sensor,angle]
        self.write_array(reg,data)

    def buzzer(self,v,t):
        self.buzz.ChangeFrequency(440)
        self.buzz.start(v)
        time.sleep(t)
        self.buzz.stop()

    def buzzer_dur(self,v,t,dur):
        end = time.time() + dur 
        while(time.time() < end):
            self.buzzer(v,t)
            time.sleep(1.0 - t)
