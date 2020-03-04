#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile


import time 
import math
import random
import urequests
import utime
import ujson
import ubinascii
# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()


#Walker Wind 2/29/20
#
#Midterm Project: Cup Pong Bot

#Initialize Motors and Distance Sensor
whacker = Motor(Port.D)
angler = Motor(Port.B)
trigger = TouchSensor(Port.S3)
looker = UltrasonicSensor(Port.S1)

#Variables
anglein = 0
firespeed = 800
actualspeed = [0]

######################################################################
#Function to trigger the ball being hit
def hit(anglein, firespeed):
    angler.reset_angle(60)
   
    angler.run_angle(50,-anglein, Stop.BRAKE)
    
    whacker.run_time(-firespeed,5000,Stop.COAST)
    
    angler.run_angle(50,anglein, Stop.BRAKE)

    return actualspeed


####################################################################
#Systemlink Code
#connect to systemlink 
Key = "o5x1NCgcRslH0MWGxNcisLHi-sYXHlRS0b10ARx7VL"   
def SL_setup():
     urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
     headers = {"Accept":"application/json","x-ni-api-key":Key}
     return urlBase, headers
     
def Put_SL(Tag, Type, Value):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     propValue = {"value":{"type":Type,"value":Value}}
     try:
          reply = urequests.put(urlValue,headers=headers,json=propValue).text
          print(reply)
     except Exception as e:
          print(e)         
          reply = 'failed'
     return reply

def Get_SL(Tag):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     try:
          value = urequests.get(urlValue,headers=headers).text
          data = ujson.loads(value)
          result = data.get("value").get("value")
     except Exception as e:
          print(e)
          result = 'failed'
     return result
     
def Create_SL(Tag, Type):
     urlBase, headers = SL_setup()
     urlTag = urlBase + Tag
     propName={"type":Type,"path":Tag}
     try:
          urequests.put(urlTag,headers=headers,json=propName).text
     except Exception as e:
          print(e)


######################################################################
def train():
    
    firespeeds = []
    for m in range(30):
        firespeeds.append(100 + m*700/30)
    actfirespeeds=firespeeds
    i=0
    while(i<30):
        if trigger.pressed()==True:
            print("The speed is: ", firespeeds[i])
            actualspeed = hit(0,firespeeds[i])
            wait(500)
            
            i=i+1
    return firespeeds


#Kinematics model: Using the equation given for trajectory
#relate a given input distance (delx) to a launch angle (anglein)
def Kinematics(delx):
    g = 9.81 #m/s^2
    dely= .225 #m
    print("X Distance is: ", delx)
    alpha = 40*math.pi/180 # in radians
    
    #for the kinematics model, keep angle constant, its impossible to solve
    numerator = .5*g*delx**2
    print(numerator)
    denominator = (dely+delx*math.tan(alpha))
    print(denominator)
    v = math.sqrt(numerator/denominator)/math.cos(alpha)
    print('Output velocity is: ', v)

    #convert firespeed from m/s to deg/s
    speed_physics= .9*(v/.105)*180/math.pi #would normally multply by -1, but using .75 to correct for error

    print("Speed calculated from physics", speed_physics)
    return speed_physics


#Model using Machine Learning: 
#Input is distance
#Output is velocity of launch

#take a bunch of data, then try to model it using ... 

#firespeeds = train()

#training data
firespeeds = []
for m in range(30):
    #print(m)
    firespeeds.append(100 + m*700/30)
#print(len(firespeeds))
distances=[.11,.13,.14,.14,.16,.17,.177,.188,.193,.206,.223,.245,.26,.274,.285,.32,.335,.356,.37,.375,.399,.417,.447,.465,.49,.496,.525,.53,.55,.59]



def LinRegression(b,m, x):
    y=0.0
    y = m*x + b
    print(y)
    return y

#values from excel for linear regression
b = -.221
m = 1363.4 
prevpress='0'
isPressed = '0'
while(True):
    prevpress = isPressed
    isPressed = Get_SL('isPressed')
    
    if isPressed is '1' and prevpress is not '1':
        dist = looker.distance()/1000
        print(dist)
        Put_SL('distance', 'STRING', str(dist))
        firespeed = int(LinRegression(b,m,looker.distance()/1000))
        #firespeed = Kinematics(dist-.06)
        Put_SL('speed', 'STRING', str(firespeed))
        
        actualspeed = hit(0,firespeed)
        wait(500)
        
        
    









# do a linear regression 

## the functions cal_mean, cal_variance, cal_covariance, cal_simple_linear_regression were found 
##from this website https://dataaspirant.com/2017/02/15/simple-linear-regression-python-without-any-machine-learning-libraries/

def cal_mean(readings):
    """
    Function to calculate the mean value of the input readings
    :param readings:
    :return:
    """
    readings_total = sum(readings)
    number_of_readings = len(readings)
    mean = readings_total / float(number_of_readings)
    return mean

def cal_variance(readings):
    """
    Calculating the variance of the readings
    :param readings:
    :return:
    """
 
    # To calculate the variance we need the mean value
    # Calculating the mean value from the cal_mean function
    readings_mean = cal_mean(readings)
    # mean difference squared readings
    mean_difference_squared_readings = [math.pow((reading - readings_mean),2) for reading in readings]
    variance = sum(mean_difference_squared_readings)
    return variance / float(len(readings) - 1)

def cal_covariance(readings_1, readings_2):
    """
    Calculate the covariance between two different list of readings
    :param readings_1:
    :param readings_2:
    :return:
    """
    readings_1_mean = cal_mean(readings_1)
    readings_2_mean = cal_mean(readings_2)
    readings_size = len(readings_1)
    covariance = 0.0
    for i in range(0, readings_size):
        covariance += (readings_1[i] - readings_1_mean) * (readings_2[i] - readings_2_mean)
    return covariance / float(readings_size - 1)



def cal_simple_linear_regression_coefficients(x_readings, y_readings):
    """
    Calculating the simple linear regression coefficients (B0, B1)
    :param x_readings:
    :param y_readings:
    :return:
    """
    # Coefficient W1 = covariance of x_readings and y_readings divided by variance of x_readings
    # Directly calling the implemented covariance and the variance functions
    # To calculate the coefficient W1
    w1 = cal_covariance(x_readings, y_readings) / float(cal_variance(x_readings))
 
    # Coefficient W0 = mean of y_readings - ( W1 * the mean of the x_readings )
    w0 = cal_mean(y_readings) - (w1 * cal_mean(x_readings))
    return w0, w1
#b,m = cal_simple_linear_regression_coefficients(distances,firespeeds)