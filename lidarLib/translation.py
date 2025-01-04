import cmath
from lidarLib import lidarMeasurment
from lidarLib.util import polarToCart, cartToPolar
class translation:
    """class to translate lidarMeasurments from one 0,0 to another"""
    def __init__(self, r:float, theta:float, rotation:float):
        """creates a translation using polar coordinates. if cartisian coordinates are prefered use the translation from Cart helper method"""
        self.r=r
        self.theta=theta
        self.rotation=rotation
        self.x, self.y = polarToCart(self.r, self.theta)

    @classmethod 
    def default(self):
        """creates a translation that will translate a point from that point back to itself. good for values where a translation object is needed but a actual translation is not"""
        return self(0,0,0)
        
        


    def applyTranslation(self, lidarPoint:lidarMeasurment)->None:
        """Applys a translation to the given point, the translation will be applyed in place"""
        lidarPoint.angle=(lidarPoint.angle+self.rotation)%360
        
        lidarPoint.distance, lidarPoint.angle = cartToPolar(lidarPoint.getX()+self.x, lidarPoint.getY()+self.y)


    def combineTranslation(self, translation:"translation")->"translation":
        """Combines to translations. the composit tranlsation will be returned"""
        return translationFromCart(self.x+translation.x, self.y+translation.y, (self.rotation+translation.rotation)%360)


def translationFromCart(x:float, y:float, rotation:float)->translation:
    """creates a translation from cartisian coordinates"""
    r, theta = cartToPolar(x, y)
    return translation(r, theta, rotation)