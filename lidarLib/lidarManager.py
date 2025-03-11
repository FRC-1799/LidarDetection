import signal
import multiexit
from multiprocessing import Pipe, Process
from lidarLib import *
from lidarLib.Lidar import Lidar
from lidarLib.lidarMap import lidarMap
from lidarLib.lidarPipeline import dataPacket, dataPacketType, lidarPipeline
import time

from lidarLib.translation import translation

def lidarManager(pipeline:"lidarPipeline", lidarArgs:list, localTranslation:translation):
    pipeline:"lidarPipeline"=pipeline
    lidar:Lidar = Lidar(*lidarArgs)
    lidar.setCurrentLocalTranslation(localTranslation)


    multiexit.register(lidar.disconnect)
    quitCount=0
    timesReset=0
    
    connectionArgs:list = None
    start =time.perf_counter()

    while pipeline.shouldLive:
        
        

        if not pipeline.isConnected():
            break


        if not lidar.isRunning() and lidar.isConnected():
            lidar.startScan()
            quitCount+=100
            if quitCount>10000:
                lidar.disconnect()

                timesReset+= 1
                pipeline.sendData(dataPacket(dataPacketType.quitWarning), timesReset)
                time.sleep(0.001)

                lidar:Lidar = Lidar(*lidarArgs)
                lidar.setCurrentLocalTranslation(localTranslation)
                lidar.connect(connectionArgs)
                lidar.setMotorPwm(500)
                lidar.startScan()

        else:
            quitCount-=1
        

        if pipeline.getDataPacket(dataPacketType.translation):
            lidar.setCurrentGlobalTranslaisConnectedtion(pipeline.getDataPacket(dataPacketType.translation))
        


        for action in pipeline.getActionQue():
            if (action.function==Lidar.connect):
                connectionArgs = action.args
            
            if action.returnType==-1:
                action.function(lidar, *action.args)
            else:
                pipeline.sendData(dataPacketType(action.returnType, action.function(lidar, *action.args)))

        
        pipeline.sendMap(lidar.lastMap)

        if (start+0.02-time.perf_counter())>0:
            time.sleep(start+0.02-time.perf_counter())
        start+=0.02

    lidar.disconnect()




def makePipedLidar(debugMode:bool, deadband:list[int], lidarTranslation:translation)->tuple[Process, "lidarPipeline"]:
    """
        Creates a seperate prosses that handles all rendering and can be updated via a pipe(connection)
        returns a tuple with the first argument being the process, this can be use cancle the process but the primary use is to be saved so the renderer doesnt get collected
        the second argument is one end of a pipe that is used to update the render engine. this pipe should be passed new lidar maps periodicly so they can be rendered. 
        WARNING all code that deals with the pipe should be surrounded by a try except block as the pipe will start to throw errors whenever the user closes the render machine.
    """
    returnPipe, lidarPipe = Pipe(duplex=True)
    returnPipe=lidarPipeline(returnPipe)
    lidarPipe=lidarPipeline(lidarPipe)
    process= Process(target=lidarManager, args=(lidarPipe, [debugMode, deadband], lidarTranslation), daemon=True)
    
    try:
        multiexit.install()
    except RuntimeError as e:
        print(e)
    process.start()


    return process, returnPipe

    