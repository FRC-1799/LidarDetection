from lidarLib import lidarMeasurment
from lidarLib.Lidar import Lidar
from lidarLib.translation import translation

class lidarMap:
    def __init__(self, hostLidar:Lidar, mapID=0, deadband=None, sensorThetaOffset=0):
        
        self.points={}
        self.deadband=deadband
        self.deadbandRaps= deadband != None and deadband[0]>deadband[1]
        self.sensorThetaOffset=sensorThetaOffset
        self.hostLidar=hostLidar
        self.isFinished=False
        self.mapID=mapID
        self.len=0
        self.startTime=None
        self.endTime=None
        

    def __array__(self):
        return self.getPoints()
    
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['hostLidar']
        return state
    
    def __setstart__(self, state):
        self.__dict__.update(state)
        self.hostLidar=None


    def addVal(self, point:lidarMeasurment, translation: translation, printFlag=False)->None:
        
        if self.startTime==None:
            self.startTime=point.timeStamp

        if point.start_flag:
            self.endTime=point.timeStamp
            self.hostLidar.mapIsDone()
            return

        if point.quality==0 or point.distance==0:
            return
        
        if self.deadband:
            if self.deadbandRaps:
                if (point.angle+self.sensorThetaOffset)%360>self.deadband[0] or (point.angle+self.sensorThetaOffset)%360<self.deadband[1]:
                    return
            else:
                if (point.angle+self.sensorThetaOffset)%360>self.deadband[0] and (point.angle+self.sensorThetaOffset)%360<self.deadband[1]:
                    return

        if translation !=None:
            translation.applyTranslation(point)

        # if printFlag:
        #     print("valHasBeenAdded", point)

             

        
        self.len+=1
        self.points[point.angle]=point

        
    

    def fetchPointAtClosestAngle(self, angle:float)->lidarMeasurment:
        if len(self.points)==0:
            return None
        return self.points[min([key for key, value in self.points.items()], key=lambda value: abs(value - angle))]
    
    def getDistanceBetweeClosestAngle(self, angle:float)->float:
        return abs(self.fetchPointAtClosestAngle(angle).angle-angle)
    
    def getPoints(self)->list[lidarMeasurment]:
        return list(self.points.values())
    

    def printMap(self)->None:
        print("current map:")
        #self.thisFuncDoesNothing()
        for point in self.getPoints():
            print(point)
            pass

    def getRange(self)->float:
        if len(self.points)==0:
            return 0
        return abs(self.fetchPointAtClosestAngle(0).angle - self.fetchPointAtClosestAngle(180).angle)*2
    
    def getPeriod(self)->float:
        if self.startTime and self.endTime:
            return self.endTime-self.startTime
        print(self.startTime, self.endTime)
        return 0
    def getHz(self)->float:
        if self.startTime and self.endTime:
            return 1/self.getPeriod()
        return 0


    def setOffset(self, theta:float)->None:
        if theta>=0 and theta<360:
            self.sensorThetaOffset=theta
        
        else:
            raise ValueError("attempted to set a sensor offset that is not a degree value: ", theta)
        
    def setDeadband(self, deadband:list)->None:
        self.deadband=deadband
        self.deadbandRaps= deadband != None and deadband[0]>deadband[1]