import cmath
class translation:

    def __init__(self, r, omega, rotation):
        self.r=r
        self.omega=omega
        self.rotation=rotation
        self.x, self.y - cmath.rect(self.rotation, self.rotation)

    def __init__(self):
        self.r=0
        self.omega=0
        self.roation=0
        self.x, self.y = 0,0


    def applyTranslation(self, lidarPoint):
        lidarPoint.angle=(lidarPoint.angle+self.rotation)%360
        
        lidarPoint.distance, lidarPoint.angle = cmath.polar(lidarPoint.getX()+self.x, lidarPoint.getY()+self.y)


    def combineTranslation(self, translation):
        return translationFromCart(self.x+translation.x, self.y+translation.y, (self.roation+translation.rotation)%360)


def translationFromCart(x, y, rotation):
    r, omega = cmath.polar(x, y)
    return translation(r, omega, rotation)