
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
from lidarHitboxingMap import lidarHitboxMap
import multiexit





def session(ntPublisher:publisher, shouldLiveSupplier:callable):
    print("session started")
    process0, lidar0 = lidarManager.makePipedLidar(False, None, translation.fromCart(5000,5000,0))
    lidar0.connectSmart(port="/dev/lidar0", baudrate=256000, timeout=3, pwm=500)
    
    lidars = [lidar0]
    time.sleep(5)
    


    # cartRenderer, cartPipe = initMachine(1)
    # polarRenderer, polarPipe = initMachine(0)
    
    while shouldLiveSupplier():
        hitboxMap:lidarHitboxMap = lidarHitboxMap()
        pointMap=[]
        lidarTranslations = []
        for lidar in lidars:
            if lidar.isConnected():
                lidar.addTanslation(ntPublisher.getPoseasTran())
                hitboxMap.addMap(lidar.getMap())
                pointMap = pointMap+lidar.getMap().getPoints()
                lidarTranslations.append(lidar.getTranslation())
                
        
        ntPublisher.publishHitboxesFromHitboxMap(hitboxMap)
        ntPublisher.publishPointsFromLidarMeasurments(pointMap)
        ntPublisher.publishLidarPosesFromTrans(lidarTranslations)


    for lidar in lidars:
        lidar.sendQuitReqeust()
    time.sleep(1)
    print("session terminated")

    

def main():
    multiexit.install()
    ntPublisher = publisher()
    thread = threading.Thread(target=session, daemon=True, kwargs={"ntPublisher":ntPublisher, "shouldLiveSupplier":ntPublisher.isConnected})
    
    


    while True:
        print("while cycle")
        if (ntPublisher.isConnected()or constants.overrideNTConnectionRequirment) and not thread.is_alive():
            thread = threading.Thread(target=session, daemon=True, kwargs={"ntPublisher":ntPublisher, "shouldLiveSupplier":ntPublisher.isConnected})
            thread.start()
            

        if (not ntPublisher.isConnected() and not constants.overrideNTConnectionRequirment) and thread.is_alive():
            thread.join(5)
            if thread.is_alive:
                print("Lidar thread did not properly terminate")
            
        
        time.sleep(5)
            

            


if __name__ == '__main__':
    main()