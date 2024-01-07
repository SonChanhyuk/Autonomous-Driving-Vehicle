#!/usr/bin/env python
# coding: utf-8

import cv2
import numpy as np
import car
import colorsensor
import time
import ultrasonic
import math
import threading
import tracking

# video test
def video():
    camera = cv2.VideoCapture(-1)
    camera.set(3,640)
    camera.set(4,480)
    
    while( camera.isOpened() ):
        _, image = camera.read()
        
        #image = image[300:, :]
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(5, 5), 0)
        
        ret, thresh1 = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)
        
        thresh_3ch = np.repeat(thresh1[:,:,np.newaxis],3,-1)
        concat_image = np.concatenate((image,thresh_3ch),axis=1)
        
        cv2.imshow('camera', concat_image)
        print(check_pos(camera))
        
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()

# check position : True : outer or False : inner
def check_pos(camera): 
    _, image = camera.read()
    image = image[300:, :]
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5, 5), 0)
    
    ret, blur_image = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)
    total = np.sum(blur_image.T,axis=1)
    size = len(total)
    
    print(np.sum(total[:size//2]), np.sum(total[size//2:]), size)
    return np.sum(total[:size//2]) < np.sum(total[size//2:])
      
FONT = cv2.FONT_HERSHEY_DUPLEX
BLUE = (255,0,0)
GREEN = (0,255,0)
RED = (0,0,255)
FILTER_RATIO = 0.85
def get_contours(img, min_area, is_simple=False):
    if is_simple:
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    result = []

    for cnt in contours:
        if cv2.contourArea(cnt) > min_area:
            result.append(cnt)

    return result


def is_circle(cnt):
    cnt_length = cv2.arcLength(cnt, True)
    cnt_area = cv2.contourArea(cnt)

    ratio = 4 * math.pi * cnt_area / pow(cnt_length, 2)

    if ratio > FILTER_RATIO:
        return True
    else:
        return False


def draw_points(img, cnt, epsilon, color):
    cnt_length = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon * cnt_length, True)

    for point in approx:
        cv2.circle(img, (point[0][0], point[0][1]), 3, color, -1)

def setLabel(img, pts, label):
    (x, y, w, h) = cv2.boundingRect(pts)
    pt1 = (x, y)
    pt2 = (x + w, y + h)
    cv2.rectangle(img, pt1, pt2, (0, 255, 0), 2)
    cv2.putText(img, label+str((w,h)), (pt1[0], pt1[1] - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255))


def sign_video():
    camera = cv2.VideoCapture(-1)
    camera.set(3,640)
    camera.set(4,480)
    while( camera.isOpened() ):
        _, img = camera.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        filter_img_red = cv2.inRange(img, (0, 0, 50), (80, 80, 255))  
        filter_img_green = cv2.inRange(img, (0, 40, 0), (90, 255, 50)) 
        filter_img = cv2.bitwise_or(filter_img_red, filter_img_green)

        contours_simple = get_contours(filter_img, 50, True)

        simple_text = "contours count : " + str(len(contours_simple))
        simple_img = cv2.putText(img.copy(), simple_text, (0, 25), FONT, 1, RED)
        for cnt in contours_simple:
            cv2.drawContours(simple_img, cnt, -1, BLUE, 5)
            if is_circle(cnt):
                draw_points(simple_img, cnt, 0.1, RED)
            else:
                draw_points(simple_img, cnt, 0.1, GREEN)
                epsilon = 0.02 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                vtc = len(approx)

                if vtc == 3:
                    setLabel(simple_img, cnt, 'Triangle')
                elif vtc == 4:
                    setLabel(simple_img, cnt, 'Rectangle')
                if(vtc == 3 or vtc == 4):
                    sign = None
                    (x, y, w, h) = cv2.boundingRect(cnt)
                    w_r = w / 640
                    h_r = h / 480
                    if (h_r > 0.1 and h_r < 0.3 and w_r > 0.1 and w_r < 2.5):
                        if (w / h < 1.2 and w / h > 0.8): sign = 1
                        elif (w / h < 1.8 and w / h > 1.2): sign = 0
                        print(sign)

    #cv2.imshow("origin image", img)
    #cv2.imshow("filter image", filter_img)
        cv2.imshow("simple image", simple_img)
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()
    
    
def sign_shape_detect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    filter_img_red = cv2.inRange(img, (0, 0, 70), (80, 80, 255))  
    filter_img_green = cv2.inRange(img, (0, 50, 0), (120, 255, 140)) 
    filter_img = cv2.bitwise_or(filter_img_red, filter_img_green)

    contours_simple = get_contours(filter_img, 50, True)
    sign = None
    for cnt in contours_simple:
        if not is_circle(cnt):
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            vtc = len(approx)

            if (vtc == 3 or vtc == 4):
                (x, y, w, h) = cv2.boundingRect(cnt)
                w_r = w / 640
                h_r = h / 480
                print(w,h,w_r,h_r)
                if (h_r > 0.04 and h_r < 0.3 and w_r > 0.04 and w_r < 0.2):
                    if (w / h < 1.2 and w / h > 0.8): sign = 1
                    elif (w / h < 1.8 and w / h > 1.2): sign = 0
    return sign        

# main code
def run():
    default_speed = 40
    speed = default_speed
    
    camera = cv2.VideoCapture(0)
    camera.set(3,640)
    camera.set(4,480)
    
    bot = car.Car()
    bot.servo(3,130)
    bot.servo(4,90)
    bot.buzzer_init()
    
    cs = colorsensor.ColorSensor() # color sensor
    cs.check()

    us = ultrasonic.Ultrasonic()
    us.check()
    
    ts = tracking.TrackingSensor()
    ts.check()
    
    mode = check_pos(camera) # True : outer, False : inner
    if (mode) :
        print("outer")
    else:
        print("inner")
    time.sleep(3.0)

    print("turn camera")
    bot.servo(3,80)
    bot.servo(4,20)   
    
    # True -> outer : green, inner : white, False -> the opposite
    print(mode)
    time.sleep(1.0)
    
    bot.run(speed,speed)
    
    speed_changed = False
    sign_detected = False
    trigger_time = 0.0
    # 0 : parking, 1 : sliipery, 2 : obstacle, 3 : slip now
    trigger_type = 0
    
    lap = 1 

    while(1):
        # UltraSonic
        if (us.check() < 30):
            print("Ultra sonic detect!")
            change_road(mode,camera,bot,speed)
            mode = not mode
            sign_detected = True
            trigger_time = time.time() + 2.0
            trigger_type = 2

        # Camera Sign Detect
        if not sign_detected:
            _, img = camera.read()
            sign = sign_shape_detect(img)
            print(sign)
            if (sign != None and not (sign == 0 and lap == 1)):
                print("sign detected! :",sign)
                
                sign_detected = True
                trigger_type = sign
                trigger_time = time.time() + 5.0 
                     
        elif (sign_detected and trigger_time < time.time()):
            sign_detected = False
            if (trigger_type == 0 and lap == 2):
                trigger_type = 0
                print("parking now")
                parking(cs,bot,default_speed)
                bot.stop()
                break
            elif (trigger_type == 1):
                #slippery
                print("slippery road now")
                trigger_type = 3
                thread = threading.Thread(target=bot.buzzer_dur,args=(30,0.3,5.0))
                thread.start()
                sign_detected = True
                speed = speed // 2
                trigger_time = time.time() + 5.0
                continue
            elif (trigger_type == 2):
                trigger_type = 0
                change_road(mode,camera,bot,speed)
                mode = not mode
            elif (trigger_type == 3):
                trigger_type = 0
                speed = default_speed
                bot.run(speed,speed)
                
            trigger_type = 0

        # Tracking Sensor
        ts_value = ts.check()
        print("ts :",ts_value)
        if (ts_value == 0):
            bot.run(default_speed * 1,default_speed // 4)
            time.sleep(1.0)
        elif (ts_value == 1):
            bot.run(default_speed // 4,default_speed * 1)
            time.sleep(1.0)

        # Color Sensor
        rgb = cs.check()
        print("rgb :",rgb)
        if (cs.isBlack(rgb)):
            print("black")
            if (speed_changed):
                bot.run(default_speed,default_speed)
                speed_changed = False
                
        elif (cs.isWhite(rgb)):
            print("white")
            if(mode):
                bot.run(default_speed // 4,default_speed * 1)
            else:
                bot.run(default_speed * 1,default_speed // 4)
                time.sleep(1.0)
            speed_changed = True
           
        elif (cs.isGreen(rgb)):
            print("green")
            if(mode):
                bot.run(default_speed * 1,default_speed // 4)
            else:
                bot.run(default_speed // 4,default_speed * 1)
            speed_changed = True
            
        elif (cs.isRed(rgb)):
            print("red")
            if(lap == 1):
                lap += 1
                mode = change_road(mode,camera,bot,default_speed)
            else:
                bot.stop()
                break
                
        elif (cs.isBlue(rgb)):
            print("blue")
            bot.stop()
            time.sleep(3.0)
            bot.run(default_speed,default_speed)
            time.sleep(0.5)
           
        elif (cs.isYellow(rgb)):
            print("yellow")
            bot.run(default_speed//2,default_speed//2)
            time.sleep(3.0)
            bot.run(speed,speed)
            
        else:
            if (speed_changed and trigger_type != 3):
                bot.run(default_speed,default_speed)
                speed_changed = False

    return 1

# True : out -> in, False : in -> out
def change_road(mode, camera, bot, speed):
    if (mode):
        bot.run(speed * 3,speed // 2)
        time.sleep(0.5)
        bot.run(speed,speed)
        time.sleep(0.5)
    else:
        bot.run(speed // 2,speed * 3)
        time.sleep(0.5)
        bot.run(speed,speed)
        time.sleep(0.5)
    return not mode
    
    
def parking(cs,bot,speed):
    bot.turn_left(speed)
    time.sleep(2.3)
    bot.back(speed,speed)
    time.sleep(2.0)
    while(True):
        if (not cs.isWhite(cs.check()) and cs.isGreen(cs.check())):
            print("stop")
            break
    bot.stop()
    
def color_test(color_sensor):
    while(1):
        rgb = color_sensor.check() 
        print(rgb)
        print("red :",color_sensor.isRed(rgb))
        print("green :",color_sensor.isGreen(rgb))
        print("blue :",color_sensor.isBlue(rgb))
        print("yellow :",color_sensor.isYellow(rgb))
        print("white :",color_sensor.isWhite(rgb))
        print("black :",color_sensor.isBlack(rgb))

        time.sleep(1.0)

if __name__ == '__main__':
    print("Start...")
    #sign_video()
    #video()
    
    #bot.buzzer_dur(50,0.3,3)
    #t = threading.Thread(target=bot.buzzer_dur,args=(20,0.3,5))
    #t.start()
    #run()
    try:
        run()
    except:
        bot = car.Car()
        bot.stop()
        
    #color_sensor = colorsensor.ColorSensor()
    #color_test(color_sensor)
        
