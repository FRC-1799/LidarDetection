import cmath
from lidarLib.util import polarToCart
class translation:

    def __init__(self, r, theta, rotation):
        self.r=r
        self.theta=theta
        self.rotation=rotation
        self.x, self.y = polarToCart(self.r, self.theta)
        
    def __init__(self):
        self.r=0
        self.theta=0
        self.rotation=0
        self.x=0
        self.y=0
        


    def applyTranslation(self, lidarPoint):
        lidarPoint.angle=(lidarPoint.angle+self.rotation)%360
        
        lidarPoint.distance, lidarPoint.angle = polarToCart(lidarPoint.getX()+self.x, lidarPoint.getY()+self.y)


    def combineTranslation(self, translation):
        return translationFromCart(self.x+translation.x, self.y+translation.y, (self.roation+translation.rotation)%360)


def translationFromCart(x, y, rotation):
    r, theta = polarToCart(x, y)
    return translation(r, theta, rotation)