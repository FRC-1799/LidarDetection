import cmath
from lidarLib import lidarMeasurment
from lidarLib.util import polarToCart, cartToPolar
class translation:

    def __init__(self, r:float, theta:float, rotation:float):
        self.r=r
        self.theta=theta
        self.rotation=rotation
        self.x, self.y = polarToCart(self.r, self.theta)

    @classmethod 
    def default(self):
        return self(0,0,0)
        
        


    def applyTranslation(self, lidarPoint:lidarMeasurment)->None:
        lidarPoint.angle=(lidarPoint.angle+self.rotation)%360
        
        lidarPoint.distance, lidarPoint.angle = cartToPolar(lidarPoint.getX()+self.x, lidarPoint.getY()+self.y)


    def combineTranslation(self, translation:translation)->translation:
        return translationFromCart(self.x+translation.x, self.y+translation.y, (self.rotation+translation.rotation)%360)


def translationFromCart(x:float, y:float, rotation:float)->translation:
    r, theta = cartToPolar(x, y)
    return translation(r, theta, rotation)