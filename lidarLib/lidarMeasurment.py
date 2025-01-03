import cmath
import time
from lidarLib.util import polarToX, polarToY

class lidarMeasurement:

    def __init__(self, raw_bytes=None, measurement_hq=None):
        
        self.timeStamp=time.time()

        if raw_bytes is not None:
            self.start_flag = bool(raw_bytes[0] & 0x1)
            self.quality = raw_bytes[0] >> 2
            self.angle = ((raw_bytes[1] >> 1) + (raw_bytes[2] << 7)) / 64.0
            self.distance = (raw_bytes[3] + (raw_bytes[4] << 8)) / 4.0
            
        elif measurement_hq is not None:
            self.start_flag=True if measurement_hq.start_flag==0x1 else False
            self.quality=measurement_hq.quality
            self.angle = ((measurement_hq.angle_z_q14*90)>>8)/64.0
            self.distance= (measurement_hq.dist_mm_q2)/4.0

    @classmethod
    def default(cls, start_flag:bool, quality:int, angle:float, distance:float)->lidarMeasurement:
        new = cls()
        new.start_flag=start_flag
        new.quality=quality
        new.angle=angle
        new.distance=distance
        return new
                
    def __str__(self):
        data = {
            "start_flag" : self.start_flag,
            "quality" : self.quality,
            "angle" : self.angle,
            "distance" : self.distance,
            "timestamp" : self.timeStamp
        }
        return str(data)

    def getAngle(self)->float:
        return self.angle

    def getDistance(self)->float:
        return self.distance

    def getX(self)->float:
        return polarToX(self.distance, self.angle)

    def getY(self)->float:
        return polarToY(self.distance, self.angle)
