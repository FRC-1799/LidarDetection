from constants import constants
from lidarHitboxNode import lidarHiboxNode

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



