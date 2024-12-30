class lidarMap:
    def __init__(self, hostLidar, endFunction = lambda map:None, mapID=0):
        
        self.points={}

        self.endFunction=endFunction
        self.hostLidar=hostLidar
        self.isFinished=False
        self.mapID=mapID
        self.len=0
        

    def __array__(self):
        return self.getPoints()

    def addVal(self, point):
        print("valHasBeenAdded", point)


        self.len+=1
        if point.quality==0:
            return


        
        if point.start_flag:
            self.hostLidar.mapIsDone()
            self.endFunction(self)
            return
        


        # if self.pointIsPastLoop(point):
        #     self.hostLidar.mapIsDone()
        #     self.endFunction(self)
        #     isFinished=True
        #     return
        self.points[point.angle]=point
        #self.thisFuncDoesNothing()


    def fetchPointAtClosestAngle(self, angle):
        if self.len==0:
            return None
        return self.points[min([key for key, value in self.points.items()], key=lambda value: abs(value - angle))]
    
    def getDistanceBetweeClosestAngle(self, angle):
        return abs(self.fetchPointAtClosestAngle(angle).angle-angle)
    
    def getPoints(self):
        return list(self.points.values())
    

    def printMap(self):
        print("current map:")
        #self.thisFuncDoesNothing()
        for point in self.getPoints():
            print(point)
            pass

    def getRange(self):
        if self.len==0:
            return 0
        return abs(self.fetchPointAtClosestAngle(0).angle - self.fetchPointAtClosestAngle(360).angle)



    