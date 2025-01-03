import cmath
from lidarLib.util import polarToCart, cartToPolar
class translation:

    def __init__(self, r, theta, rotation):
        self.r=r
        self.theta=theta
        self.rotation=rotation
        self.x, self.y = polarToCart(self.r, self.theta)

    @classmethod 
    def default(self):
        return self(0,0,0)
        
        


    def applyTranslation(self, lidarPoint):
        lidarPoint.angle=(lidarPoint.angle+self.rotation)%360
        
        lidarPoint.distance, lidarPoint.angle = cartToPolar(lidarPoint.getX()+self.x, lidarPoint.getY()+self.y)


    def combineTranslation(self, translation):
        return translationFromCart(self.x+translation.x, self.y+translation.y, (self.rotation+translation.rotation)%360)


def translationFromCart(x, y, rotation):
    r, theta = cartToPolar(x, y)
    return translation(r, theta, rotation)