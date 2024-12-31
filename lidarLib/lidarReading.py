import math

class lidarReading:

    def __init__(self, data):
        
        self.startFlag=data[0]
        self.quality=data[1]
        self.angle=data[2]
        self.distance=data[3]


                
    def __str__(self):
        data = {
            "start_flag" : self.startFlag,
            "quality" : self.quality,
            "angle" : self.angle,
            "distance" : self.distance
        }
        return str(data)

    def getAngle(self):
        return self.angle

    def getDistance(self):
        return self.distance

    def getX(self):
        return math.cos(math.radians(self.angle))*self.distance

    def getY(self):
        return math.sin(math.radians(self.angle))*self.distance