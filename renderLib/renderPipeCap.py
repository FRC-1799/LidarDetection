from multiprocessing.connection import Connection

from lidarLib import lidarMap

class renderPipeCap:
    def __init__(self, pipe:Connection):
        self.pipe=pipe
        self.mostRecentVal=None

    def get(self)->lidarMap:
        
        while self.pipe.poll():
        
            #print("data receved")
            self.mostRecentVal = self.pipe.recv()
        #print("data updated", self.mostRecentVal.mapID)
        return self.mostRecentVal

        
    def send(self, sendable:lidarMap)->None:

        
        self.pipe.send(sendable)
