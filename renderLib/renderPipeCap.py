

class renderPipeCap:
    def __init__(self, pipe):
        self.pipe=pipe


    def get(self):
        
        if self.pipe.poll(1):
           
            return self.pipe.recv()
        

        
    def send(self, sendable):

        
        self.pipe.send(sendable)
