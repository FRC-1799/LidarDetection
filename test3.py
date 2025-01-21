#!/usr/bin/env python3
'''Animates distances and measurement quality'''
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

    renderer, pipe = initMachine()
    
    try:
        while True:
            pipe.send(lidar.lastMap)
            time.sleep(0.1)
            # print("data sent", lidar.lastMap.mapID)
    except Exception as e:
        print(e)
    
    lidar.stop()
    lidar.disconnect()
    
    print("The run is done")

if __name__ == '__main__':
    run()
