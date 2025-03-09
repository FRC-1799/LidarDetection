from constants import constants
from lidarHitboxNode import lidarHiboxNode
from lidarLib import lidarMeasurment
from lidarLib.lidarMap import lidarMap

class lidarHitboxMap:
    seed = {{}}
    

    def __init__(self, seed:list[list[bool]], xHeight:float= constants.mapHeightMeters, yWidth:float = constants.mapWidthMeters, nodeSideLen:float = constants.mapNodeSizeMeters):
        self.xHeight=xHeight
        self.yWidth=yWidth
        self.nodeSideLen=nodeSideLen
        self.nodeMap:list[list[lidarHiboxNode]]= []
        for y in range(0, yWidth, nodeSideLen):
            self.nodeMap.append([])
            for x in range(0, xHeight, nodeSideLen):
                self.nodeMap.append(lidarHiboxNode(x, y, sideLen=self.nodeSideLen))


        self.seed=seed
        for y in range(0, seed.len()):
            for x in range(0, seed[y].len()):
                self.nodeMap[y][x].setLegality(seed[y][x])
        
    def getAtMeters(self, x:int, y:int)->lidarHiboxNode:
        return self.nodeMap[y*constants.mapNodeSizeMeters][x*constants.mapNodeSizeMeters]
    
    def getAs1DList(self)->list[lidarHiboxNode]:
        returnlist=[]
        for arr in self.nodeMap:
            returnlist.extend(arr)

        return returnlist

    def addVal(self, reading:lidarMeasurment):
        self.getAtMeters(reading.getX()*constants.lidarReadingToMapVal, reading.getY()*constants.lidarReadingToMapVal).addReading(reading)


    def addMap(self, map:lidarMap):
        for reading in map.getPoints():
            self.addVal(reading)

