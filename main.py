
'''Animates distances and measurment quality'''

from multiprocessing import Process
import threading
from constants import constants
from lidarLib.lidarMeasurment import lidarMeasurement
from lidarLib.Lidar import Lidar
import matplotlib.pyplot as plot
import numpy as np
import matplotlib.animation as animation
from functools import partial
import pickle
import time
from lidarLib.translation import translation
from publisher import publisher
from renderLib.renderMachine import initMachine
from lidarLib import lidarManager
from lidarLib.lidarPipeline import lidarPipeline
import lidarHitboxingMap






def session(ntPublisher:publisher, shouldLiveSupplier:callable):
    process0, lidar0 = lidarManager.makePipedLidar(False, None, translation.fromCart(5000,5000,0))
    lidar0.connectSmart(port="/dev/lidar0", baudrate=256000, timeout=3, pwm=500)
    
    
    


    # cartRenderer, cartPipe = initMachine(1)
    # polarRenderer, polarPipe = initMachine(0)
    
    
    
    # while cartPipe.isConnected() and polarPipe.isConnected():
    #     newMap=lidarHitboxingMap.lidarHitboxMap()
    #     newMap.addMap(lidar.getMap())
    #     cartPipe.send(newMap)
    #     polarPipe.send(lidar.getMap())
    #     ntPublisher.publishHitboxesFromHitboxMap(newMap)
    #     ntPublisher.publishPointsFromLidarMeasurments(lidar.getMap().getPoints())
    #     ntPublisher.publishLidarPosesFromTrans([translation.fromCart(5000,5000,0)])
    #     time.sleep(0.1)

    
    print("session terminated")

def start()->tuple[list[lidarPipeline],list[Process]]:
    returnTuple= ([],[])


    returnTuple[0].append(lidar)
    returnTuple[1].append(process)

def stop(lidars:list[lidarPipeline], processes:list[Process]):
    for lidar in lidars:
        lidar.sendQuitReqeust()
    return (None, None)
    

def main():
    
    ntPublisher = publisher()
    thread = threading.Thread(target=session, daemon=True, kwargs=(ntPublisher, lambda:not ntPublisher.isConnected()))
    
    


    while True:
        if (ntPublisher.isConnected()or constants.overrideNTConnectionRequirment) and thread.is_alive():
            thread.start()
            

        if (not ntPublisher.isConnected() or not constants.overrideNTConnectionRequirment) and thread.is_alive():
            thread.join(5)
            if thread.is_alive:
                print("Lidar thread did not properly terminate")
            
        
        time.sleep(5)
            

            


if __name__ == '__main__':
    main()