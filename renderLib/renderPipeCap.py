from multiprocessing.connection import Connection

from lidarLib import lidarMap

class renderPipeCap:
    """class that encapsulates pipe connections between a user and the render engine"""
    def __init__(self, pipe:Connection):
        """Creates a render pipe cap surrounding the pipe input"""
        self.pipe=pipe
        self.mostRecentVal=None

    def _get(self)->lidarMap:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            returns the most recent data sent over the pipe, since the render machine never sends data this function should never be used by the user
        """
        while self.pipe.poll():
        
            #print("data receved")
            self.mostRecentVal = self.pipe.recv()
        #print("data updated", self.mostRecentVal.mapID)
        return self.mostRecentVal

        
    def send(self, sendable:lidarMap)->None:
        """Sends the inputed lidar map to the other side of the pipe(aka the render machinel)"""
        
        self.pipe.send(sendable)
