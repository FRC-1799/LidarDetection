from multiprocessing.connection import Connection

class renderPipeCap:
    def __init__(self, pipe:Connection):
        self.pipe=pipe
        self.mostRecentVal=None

    def get(self):
        
        while self.pipe.poll():
        
            #print("data receved")
            self.mostRecentVal = self.pipe.recv()
        #print("data updated", self.mostRecentVal.mapID)
        return self.mostRecentVal

        
    def send(self, sendable):

        
        self.pipe.send(sendable)
