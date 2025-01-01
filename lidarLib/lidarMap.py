class lidarMap:
    def __init__(self, hostLidar, mapID=0):
        
        self.points={}

        
        self.hostLidar=hostLidar
        self.isFinished=False
        self.mapID=mapID
        self.len=0
        

    def __array__(self):
        return self.getPoints()
    
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['hostLidar']
        return state
    
    def __setstart__(self, state):
        self.__dict__.update(state)
        self.hostLidar=None


    def addVal(self, point, printFlag=False):
        if printFlag:
            print("valHasBeenAdded", point)


        
        if point.quality==0:
            return

        self.len+=1


        
        if point.start_flag:
            self.hostLidar.mapIsDone()
           
            return
        


        # if self.pointIsPastLoop(point):
        #     self.hostLidar.mapIsDone()
        #     self.endFunction(self)
        #     isFinished=True
        #     return
        self.points[point.angle]=point
        #self.thisFuncDoesNothing()


    def fetchPointAtClosestAngle(self, angle):
        if len(self.points)==0:
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
        if len(self.points)==0:
            return 0
        return abs(self.fetchPointAtClosestAngle(0).angle - self.fetchPointAtClosestAngle(360).angle)



    