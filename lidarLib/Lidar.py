
from time import sleep
from lidarLib.lidarReading import lidarReading
from lidarLib.pyrplidarSerial import PyRPlidarSerial
from lidarLib.lidarProtocol import *
import lidarLib.lidarProtocol
from adafruit_rplidar import RPLidar
from lidarLib.lidarMap import lidarMap
import threading
from typing import Tuple, Dict, Any, Optional, List, Iterator, Union
from busio import UART
from digitalio import DigitalInOut



class Lidar(RPLidar):

    def __init__(self, MotorPin: DigitalInOut=None, Port = "/dev/ttyusb0", Baudrate: int = 256000, Timeout: float = 3, Logging: bool = False,):
        
        self.currentMap=lidarMap(self)
        self.lastMap=lidarMap(self)
        self.isDone=False
        super().__init__(MotorPin, Port, timeout=Timeout, baudrate=Baudrate, logging=Logging)
        #self.eventLoop()
        
        
        

    
    def __del__(self):
        
        self.disconnect()
        


    def disconnect(self):
        
        self.stop_motor()
        self.stop()
        super().disconnect()
            
           

    def update(self):
        while True:
            for scan in self.iter_measurements():
                
                self.currentMap.addVal(lidarReading(scan))
            
        



    def start(self, scan_type=0, startThreaded=True):
        
        
        if startThreaded:
            self.loop = threading.Thread(target=self.update, daemon=True)
            self.loop.start()

        super().start(scan_type=scan_type)
    

    def stop(self):
        self.loop._stop()
        super().stop()

    
    def mapIsDone(self):
        print("map swap attempted")
        self.lastMap=self.currentMap
        self.currentMap=lidarMap(self, mapID=self.lastMap.mapID+1)
        print(len(self.lastMap.getPoints()),self.lastMap.len, self.lastMap.mapID, self.lastMap.getRange())
        print(len(self.currentMap.getPoints()),self.currentMap.len ,self.currentMap.mapID)
        
        #print(self.currentMap.points==self.lastMap.points)



