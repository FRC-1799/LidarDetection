class lidarMap:
    def __init__(self, hostLidar, startPoint=0, endFunction = lambda map:None, seedPoints={}):
        
        self.points=seedPoints
        self.startPoint=startPoint
        self.lastPoint=startPoint
        self.endFunction=endFunction
        self.hostLidar=hostLidar
        self.isFinished=False

    def __array__(self):
        return self.getPoints()

    def addVal(self, point):
        print("valHasBeenAdded")
        if self.pointIsPastLoop(point):
            self.hostLidar.mapIsDone()
            self.endFunction(self)
            isFinished=True
            return
        self.points[point.angle]=point


    def pointIsPastLoop(self, point):
        if point.angle<self.lastPoint.angle:
            return point.angle>self.startPoint.angle
        else:
            return self.startPoint.angle>self.lastPoint.angle and self.startPoint.angle<point.angle

    def fetchPointAtClosestAngle(self, angle):
        return min(self.points.items(), key=lambda _, value: abs(value - angle))[1]
    
    def getDistanceBetweeClosestAngle(self, angle):
        return abs(min(self.points.items(), key=lambda _, value: abs(value - angle))[1].angle-angle)
    
    def getPoints(self):
        return list(self.points.values())
    

    def printMap(self):
        print("current map:")
        for point in self.points:
            print(point)
    

    