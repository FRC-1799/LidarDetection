from lidarLib import *
from lidarLib.Lidar import Lidar
from lidarLib.lidarPipeline import lidarPipeline, dataPacketType
import time

from lidarLib.translation import translation

def lidarManager(pipeline:lidarPipeline, lidarArgs:list, localTranslation:translation):
    pipeline:lidarPipeline=pipeline
    lidar:Lidar = Lidar(*lidarArgs)
    lidar.setCurrentLocalTranslation(localTranslation)
    lidar.setMotorPwm(500)
    lidar.startScan()
    

    


    while pipeline.shouldLive:
        start =time.perf_counter()
        
        lidar.setCurrentGlobalTranslation(pipeline.getDataPacket(dataPacketType.translation))
        


        for action in pipeline.getActionQue():
            if action.returnType==-1:
                action.function(lidar, *action.args)
            else:
                pipeline.sendData(dataPacketType(action.returnType, action.function(lidar, *action.args)))


        pipeline.sendMap(lidar.lastMap)


        time.sleep(start+0.02-time.perf_counter())

