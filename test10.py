#!/usr/bin/env python3
'''Animates distances and measurement quality'''
import math
from lidarLib.lidarMeasurment import lidarMeasurement
from lidarLib.Lidar import Lidar
import matplotlib.pyplot as plot
import numpy as np
import matplotlib.animation as animation
from functools import partial
import pickle
import time
from lidarLib.translation import translation
from renderLib.renderMachine import initMachine

# Update the port name to match macOS's serial device naming
PORT_NAME = "/dev/tty.usbserial-2110"  # Replace with the actual device name
DMAX = 1600
IMIN = 20
IMAX = 20
SIZEOFMAPITEM=0.3


def run():
    lidar = Lidar(debugMode=True, deadband=None)
    # Update the port name for macOS
    lidar.connect(port=PORT_NAME, baudrate=256000, timeout=3)
    lidar.setMotorPwm(500)
    
    lidar.getScanModes()
    print(lidar.getSampleRate())
    print(lidar.getScanModeTypical())
    # lidar.startScanExpress(3)
    lidar.startScan()
    time.sleep(2)

    #renderer, pipe = initMachine()
    funnyFunc(lidar)

    try:
        while True:
            #pipe.send(lidar.lastMap)
            time.sleep(0.1)
            funnyFunc(lidar)
            # print("data sent", lidar.lastMap.mapID)
    except Exception as e:
        print(e)
    



    lidar.stop()
    lidar.disconnect()
    
    print("The run is done")




def funnyFunc(lidar:Lidar):
    map = []
    map = initList(map, 500, [])
    i=0
    print(map)
    for subArr in map:
        map[i]=initList(subArr, 500, False)
        i+=1

    for point in lidar.lastMap.getPoints():
        cartVals  = point.getCart()    
        print(map)
        map[math.floor(cartVals[0]/SIZEOFMAPITEM)][math.floor(cartVals[1]/SIZEOFMAPITEM)] = True
    

    for subArr in map:
        print(subArr)

def initList(startList: list, items: int, val:any)->list:
    list = []
    for i in range(items):
        list.append(val)

    return list


if __name__ == '__main__':
    run()