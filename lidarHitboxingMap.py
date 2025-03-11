import math
from constants import constants
from lidarHitboxNode import lidarHiboxNode
from lidarLib import lidarMeasurment
from lidarLib.lidarMap import lidarMap

class lidarHitboxMap:
    
    adjecencyList=[[0, 1],[0, -1],[1, 0],[-1, 0]]    

    def __init__(self, seed:list[list[bool]] =constants.map, xHeight:float= constants.mapHeightMeters, yWidth:float = constants.mapWidthMeters, nodeSideLen:float = constants.mapNodeSizeMeters):
        self.xHeight=xHeight
        self.yWidth=yWidth
        self.nodeSideLen=nodeSideLen
        self.nodeMap:list[list[lidarHiboxNode]]= []
        self.clumps=0
        for y in range(math.ceil(yWidth/nodeSideLen)):
            self.nodeMap.append([])
            for x in range(math.ceil(xHeight/nodeSideLen)):
                
                self.nodeMap[-1].append(lidarHiboxNode(x*nodeSideLen, y*nodeSideLen, sideLen=self.nodeSideLen))


        self.seed=seed
        for y in range(0, len(seed)):
            for x in range(0, len(seed[y])):
                print(y," ", x)
                self.nodeMap[y][x].setLegality(seed[y][x])
        
    def getAtMeters(self, x:int, y:int)->lidarHiboxNode:
        return self.nodeMap[math.floor(y*constants.mapNodeSizeMeters)][math.floor(x*constants.mapNodeSizeMeters)]
    
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


    def clumpify(self):
        self.clumps=[]
        for row in self.nodeMap:
            for node in row:
                node.hasBeenTouched=False

        for row in self.nodeMap:
            for node in row:
                if not node.hasBeenTouched and not node.isOpen:
                    
                    self.clumps.append([])
                    
                    que=[node]
                    while que.len!=0:
                        current = que[0]
                        self.clumps[-1].append(current)
                        for side in self.adjecencyList:
                            try:
                                new:lidarHiboxNode = self.nodeMap[current.y+side[0]][current.x+side[1]]
                                new.hasBeenTouched=True
                            except IndexError:
                                continue

                            if not new.isOpen:
                                que.append(node)

                
                        




