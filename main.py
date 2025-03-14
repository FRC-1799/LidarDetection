
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






def run(ntPublisher:publisher, lidars:list[lidarPipeline]):
    
    
    
    

    # axis = subplot.scatter([0, 1], [100, 2000], s=1, c=[IMIN, IMAX],
    #                        cmap=plot.cm.Greys_r, lw=0)
    
    #lidar.setCurrentLocalTranslation(translation(0,0, 180))
    time.sleep(1)
    #lidar.currentMap.printMap()
    #print(lidar.currentMap.points)
    #lidar.currentMap.thisFuncDoesNothing()
    cartRenderer, cartPipe = initMachine(1)
    polarRenderer, polarPipe = initMachine(0)
    
    
    
    while cartPipe.isConnected() and polarPipe.isConnected():
        newMap=lidarHitboxingMap.lidarHitboxMap()
        newMap.addMap(lidar.getMap())
        cartPipe.send(newMap)
        polarPipe.send(lidar.getMap())
        ntPublisher.publishHitboxesFromHitboxMap(newMap)
        ntPublisher.publishPointsFromLidarMeasurments(lidar.getMap().getPoints())
        ntPublisher.publishLidarPosesFromTrans([translation.fromCart(5000,5000,0)])
        time.sleep(0.1)
            #print("data sent", lidar.lastMap.mapID)

            #print("data sent", lidar.lastMap.mapID)

    # ani = animation.FuncAnimation(
    # fig, partial(update_line, lidar=lidar, line=line),
    #frames=np.linspace(0, 2*np.pi, 128), blit=True)
    # for i in range(10):
    #     with open('data'+str(i)+'.pkl', 'wb') as file:
    #         pickle.dump(lidar.lastMap, file)
    #         time.sleep(2)
    
    #lidar.sendQuitReqeust()
 
    
    print("the run is done")

def start()->tuple[list[lidarPipeline],list[Process]]:
    returnTuple= ([],[])

    process, lidar = lidarManager.makePipedLidar(False, None, translation.fromCart(5000,5000,0))
    lidar.connectSmart(port="/dev/lidar0", baudrate=256000, timeout=3, pwm=500)
    returnTuple[0].append(lidar)
    returnTuple[1].append(process)

def stop(lidars:list[lidarPipeline], processes:list[Process]):
    for lidar in lidars:
        lidar.sendQuitReqeust()
    return (None, None)
    

def main():
    
    ntPublisher = publisher()
    lidars:list[lidarPipeline] = []
    processes:list[Process] = []
    isCurrent=False
    while True:
        if (ntPublisher.isConnected()or constants.overrideNTConnectionRequirment) and isCurrent==False:
            lidars, processes = start()
            isCurrent=True

        if (not ntPublisher.isConnected() or constants.overrideNTConnectionRequirment) and isCurrent:
            lidars, processes = stop(lidars, processes)
            isCurrent=False
        
        if (isCurrent):
            run(ntPublisher, lidars)
            time.sleep(0.02)

        else:
            time.sleep(5)
            

            


if __name__ == '__main__':
    main()