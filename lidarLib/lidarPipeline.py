from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

from lidarLib.lidarMap import lidarMap
from lidarLib.Lidar import Lidar
from enum import Enum

from lidarLib.lidarProtocol import RPlidarDeviceInfo
from lidarLib.translation import translation


class lidarPipeline:
    """class that encapsulates pipe connections between a user and the render engine"""
    def __init__(self, pipe:Connection, host:Process=None):
        """Creates a render pipe cap surrounding the pipe input"""
        self.__pipe=pipe
        self.__dataPackets = []
        self.host=host

        for type in dataPacketType.options:
            print(type)
            self.__dataPackets.append(None)

        self.shouldLive=True

        self.__commandQue:list[commandPacket] = []

    def __get(self)->lidarMap:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            returns the most recent data sent over the pipe, since the render machine never sends data this function should never be used by the user
        """
            
        if self.isConnected():    
            while self.__pipe.poll():
                #print("data receved")
                try:
                    mostRecentVal = self.__pipe.recv()
                    if (mostRecentVal.__class__ == dataPacket):
                        self.__dataPackets[mostRecentVal.type] = mostRecentVal.data

                    elif (mostRecentVal.__class__ == commandPacket):
                        self.__commandQue.append(mostRecentVal)

                    elif(mostRecentVal.__class__ == quitPacket):
                        self.shouldLive=False
                    
                    elif(mostRecentVal.__class__ == ping):
                        pass

                    else:
                        raise ValueError("attempted to send a value over the lidar pipline that was not of type commandPacket or dataPacket")
                
                except EOFError:
                    print("lidar pipeline missing connection")
                    return
        else:
            print("lidar pipeline missing connection")


    def close(self):
        self.__pipe.close()


    def getNextAction(self)->"commandPacket":
        self.__get()
        if (self.__commandQue.len>0):
            return self.__commandQue.pop(0)
        
        return None
    
    def peakNextAction(self)->"commandPacket":
        self.__get()
        if (self.__commandQue.len>0):
            return self.__commandQue[0]
        
        return None
    
    def getActionQue(self)->list["commandPacket"]:
        self.__get()
        temp = self.__commandQue
        self.__commandQue=[]
        return temp
    
    def peakActionQue(self)->list["commandPacket"]:
        self.__get()
        return self.__commandQue
    
    def getAllPackets(self)->list["dataPacket"]:
        self.__get()
        return self.__dataPackets
    
    def getDataPacket(self, type:int)->"dataPacket":
        self.__get()
        return self.__dataPackets[type]
    

    def sendMap(self, map:lidarMap)->None:
        """Sends the inputed lidar map to the other side of the pipe(aka the render machinel)"""
        
        self.sendData(dataPacket(dataPacketType.lidarMap, map))

    def sendTrans(self, translation:translation):
        self.sendData(dataPacket(dataPacketType.translation, translation))

    def sendSampleRate(self, sampleRate):
        self.sendData(dataPacket(dataPacketType.sampleRate, sampleRate))

    def sendScanTypes(self, scanTypes):
        self.sendData(dataPacket(dataPacketType.scanModes, scanTypes))

    def sendData(self, data:"dataPacket"):
        if (data.__class__!= dataPacket and data.type not in dataPacketType.options):
            raise ValueError("Attempted to send data over a lidar pipleine with an invalid data type packet")
        self.__pipe.send(data)

    def sendAction(self, action:"commandPacket"):
        if action.__class__ != commandPacket:
            raise ValueError("Attmpted to send action throught the lidar pipline that wasnt an action")
        self.__pipe.send(action)
    

    def sendQuitReqeust(self):
        self.__get()
        self.__pipe.send(quitPacket())

    def isConnected(self)->bool:
        try:
            self.__pipe.send(ping())
        except EOFError as e:
            print("pipe closure detected")
            return False



        return True


    def isRunning():
        # TODO
        pass

    def disconnect(self, leaveRunning=False)->None:
        self.sendAction(commandPacket(Lidar.disconnect,[leaveRunning]))

    def stop(self)->None:
        self.sendAction(commandPacket(Lidar.stop,[]))
    
    def reset(self)->None:
        self.sendAction(commandPacket(Lidar.reset,[]))
    
    def setMotorPwm(self, pwm:int, overrideInternalValue=True)->None:
        self.sendAction(commandPacket(Lidar.setMotorPwm,[pwm, overrideInternalValue]))

    def connect(self):
        self.sendAction(commandPacket(Lidar.connect,[]))

    def getMap(self)->lidarMap:
        return self.getDataPacket(dataPacketType.lidarMap)


    def startScan(self):
        self.sendAction(commandPacket(Lidar.startScan, []))

        
    def addTanslation(self, translation:translation):
        self.sendAction(commandPacket(Lidar.setCurrentLocalTranslation, [translation]))
        self.sendAction(commandPacket(Lidar.getCombinedTrans, [], 1))

    def getTranslation(self)->translation:
        return self.__dataPackets[dataPacketType.translation]           

    def getInfo(self)->RPlidarDeviceInfo:
        return self.getDataPacket(5)




class commandPacket:
    def __init__(self, function:callable, args:list, returnType:int=-1):
        self.function = function
        self.args = args
        if returnType not in dataPacketType.options and returnType!=-1:
            raise ValueError("attmpted to make a command packet with a return type that does not exist")

        self.returnType=returnType

class dataPacketType:

    lidarMap = 0
    translation = 1
    quitWarning = 2
    sampleRate = 3
    scanModes = 4
    lidarInfo = 5
    options:list[int] = [lidarMap, translation, quitWarning, sampleRate, scanModes, lidarInfo]
    

class dataPacket():
    def __init__(self, type:int, data):
        if (type not in dataPacketType.options):
            raise ValueError("Tried to create a data packet with an invalid data type")
         
        self.type = type
        self.data=data

class quitPacket:
    pass

class ping:
    pass

