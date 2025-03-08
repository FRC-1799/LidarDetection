from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

from lidarLib import lidarManager, lidarMap
from enum import Enum

from lidarLib.translation import translation


class lidarPipeline:
    """class that encapsulates pipe connections between a user and the render engine"""
    def __init__(self, pipe:Connection):
        """Creates a render pipe cap surrounding the pipe input"""
        self.__pipe=pipe
        self.__dataPackets = []

        for type in dataPacketType.options:
            dataPacket[type] = None

        self.shouldLive=True

        self.__commandQue:list[commandPacket] = []

    def __get(self)->lidarMap:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            returns the most recent data sent over the pipe, since the render machine never sends data this function should never be used by the user
        """
        while self.__pipe.poll():
        
            #print("data receved")
            mostRecentVal = self.__pipe.recv()
            if (mostRecentVal.__class__ == dataPacket):
                self.__dataPackets[mostRecentVal.type] = mostRecentVal.data
            elif (mostRecentVal.__class__ == commandPacket):
                self.__commandQue.append(dataPacket)

            elif(mostRecentVal.__class__ == quitPacket):
                self.shouldLive=False

            else:
                raise ValueError("attempted to send a value over the lidar pipline that was not of type commandPacket or dataPacket")



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
    

    def sendMap(self, sendable:lidarMap)->None:
        """Sends the inputed lidar map to the other side of the pipe(aka the render machinel)"""
        
        self.sendData(dataPacket(dataPacketType.map, lidarMap))

    def sendData(self, data:"dataPacket"):
        if (data.__class!= dataPacket and data.type not in dataPacketType.options):
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
        return not self.__pipe.closed

    

class commandPacket:
    def __init__(self, function:function, args:list, returnType:int=-1):
        self.function = function
        self.args = args
        if returnType not in dataPacketType and returnType!=-1:
            raise ValueError("attmpted to make a command packet with a return type that does not exist")

        self.returnType=returnType

class dataPacketType(Enum):
    map = 0
    translation = 1
    quitWarning = 2
    options:list[int] = [map, translation, quitWarning]

class dataPacket():
    def __init__(self, type:int, data):
        if (type not in dataPacketType.options):
            raise ValueError("Tried to create a data packet with an invalid data type")
        
        self.type = type
        self.data=data

class quitPacket:
    pass


def makePipedLidar(args:list, lidarTranslation:translation)->tuple[Process, Connection]:
    """
        Creates a seperate prosses that handles all rendering and can be updated via a pipe(connection)
        returns a tuple with the first argument being the process, this can be use cancle the process but the primary use is to be saved so the renderer doesnt get collected
        the second argument is one end of a pipe that is used to update the render engine. this pipe should be passed new lidar maps periodicly so they can be rendered. 
        WARNING all code that deals with the pipe should be surrounded by a try except block as the pipe will start to throw errors whenever the user closes the render machine.
    """
    returnPipe, lidarPipe = Pipe(duplex=True)
    returnPipe=lidarPipe(returnPipe)
    lidarPipe=lidarPipe(lidarPipe)
    process= Process(target=lidarManager, args=(lidarPipe, args, translation))
    process.start()


    return process, returnPipe

    