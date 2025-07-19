import signal
from lidarLib.LidarConfigs import lidarConfigs
import multiexit
from multiprocessing import Pipe, Process
from lidarLib import *
from lidarLib.Lidar import Lidar
from lidarLib.lidarMap import lidarMap
from lidarLib.lidarPipeline import dataPacket, dataPacketType, lidarPipeline
import time
import stop
from lidarLib.translation import translation

def lidarManager(pipeline:"lidarPipeline", lidarConfig:lidarConfigs):
    print("Manager start")
    pipeline:"lidarPipeline"=pipeline
    lidar:Lidar = Lidar(lidarConfig)

    if (not lidarConfig.autoConnect):
        raise ValueError("piped lidars must be created with auto connect on but lidar", lidarConfig.port, "was created as piped with it off")


    pipeline._sendScanTypes(lidar.getScanModes())
    pipeline._sendSampleRate(lidar.getSampleRate())
    pipeline._sendLidarInfo(lidar.getInfo())
    pipeline._sendScanModeTypical(lidar.getScanModeTypical())
    pipeline._sendScanModeCount(lidar.getScanModeCount())


    multiexit.register(lidar.disconnect)
    quitCount=0
    timesReset=0
    
    start =time.perf_counter()

    while pipeline.shouldLive:
        
        

        if not pipeline.isConnected():
            time.sleep(0.1)
            break


        if not lidar.isRunning() and lidar.isConnected():
            lidar.startScan()
            time.sleep(5)
            quitCount+=100
            if quitCount>10000:
                lidar.disconnect()

                timesReset+= 1
                pipeline._sendData(dataPacket(dataPacketType.quitWarning), timesReset)
                time.sleep(0.001)

                lidar:Lidar = Lidar(lidarConfigs)
                lidar.connect()
                lidar.setMotorPwm(500)
                lidar.startScan()

        else:
            quitCount-=1
        

        if pipeline.getDataPacket(dataPacketType.translation):
            lidar.setCurrentGlobalTranslation(pipeline.getDataPacket(dataPacketType.translation))
        


        for action in pipeline._getActionQue():
            if action.function==Lidar.startScan:
                try:
                    action.function(lidar, *action.args)
                except:
                    lidar.stop()
                    
                    time.sleep(1)
                    lidar.lidarSerial.flush()
                    # lidar:Lidar = Lidar(*lidarArgs)
                    # lidar.setCurrentLocalTranslation(localTranslation)
                    # lidar.connect(connectionArgs)
                    
                    lidar.startScan()
 

            
            elif action.returnType==-1:
                action.function(lidar, *action.args)
            else:
                pipeline._sendData(dataPacket(action.returnType, action.function(lidar, *action.args)))

        if (lidar.getLastMap()):
            pipeline._sendMap(lidar.getLastMap())
        
        pipeline._sendTrans(lidar.getCombinedTrans())

        

        if (start+0.02-time.perf_counter())>0:
            time.sleep(start+0.02-time.perf_counter())

        
        start+=0.02

    print("lidar shut down")
    lidar.disconnect()




def makePipedLidar(lidarConfig:lidarConfigs)-> "lidarPipeline":
    """
        Creates a separate posses that handles all rendering and can be updated via a pipe(connection)
        returns a tuple with the first argument being the process, this can be use cancel the process but the primary use is to be saved so the renderer doesn't get garbage collected
        the second argument is one end of a pipe that is used to update the render engine. This pipe should be passed new lidar maps periodically so they can be rendered. 
    """


    print("manager")
    returnPipe, lidarPipe = Pipe(duplex=True)
    returnPipe=lidarPipeline(returnPipe)
    lidarPipe=lidarPipeline(lidarPipe)
    process= Process(target=lidarManager, args=(lidarPipe, lidarConfig), daemon=True)
    returnPipe.host=process
    
    try:
        multiexit.install()
    except RuntimeError as e:
        print(e)
    process.start()


    return returnPipe

    