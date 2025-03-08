from lidarLib import *
from lidarLib.Lidar import Lidar
from lidarLib.lidarPipeline import lidarPipeline, dataPacket, dataPacketType
import time

from lidarLib.translation import translation

def lidarManager(pipeline:lidarPipeline, lidarArgs:list, localTranslation:translation):
    pipeline:lidarPipeline=pipeline
    lidar:Lidar=initLidar(list, translation)
    quitCount=0
    timesReset=0

    


    while pipeline.shouldLive:
        start =time.perf_counter()

        if not lidar.isRunning():
            lidar.startScan()
            quitCount+=100
            if quitCount>10000:
                lidar.disconnect()
                timesReset+= 1
                pipeline.sendData(dataPacket(dataPacketType.quitWarning), timesReset)
                time.sleep(0.001)
                lidar = initLidar(list, translation)

        else:
            quitCount-=1
        
        lidar.setCurrentGlobalTranslation(pipeline.getDataPacket(dataPacketType.translation))
        


        for action in pipeline.getActionQue():
            if action.returnType==-1:
                action.function(lidar, *action.args)
            else:
                pipeline.sendData(dataPacketType(action.returnType, action.function(lidar, *action.args)))


        pipeline.sendMap(lidar.lastMap)


        time.sleep(start+0.02-time.perf_counter())

def initLidar(lidarArgs:list, localTranslation:translation)->Lidar:
    lidar:Lidar = Lidar(*lidarArgs)
    lidar.setCurrentLocalTranslation(localTranslation)
    lidar.setMotorPwm(500)
    lidar.startScan()
    return lidar