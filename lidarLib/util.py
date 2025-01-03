import math

def polarToCart(r:float,theta:float)->tuple:
    return polarToX(r, theta), polarToY(r, theta)

def cartToPolar(x:float, y:float)->tuple:
    deg=math.degrees(math.atan2(y,x))
    if deg<0:
        deg+=360
    return math.sqrt(x**2+ y**2), deg

def polarToX(r:float, theta:float)->float:
    return r*math.cos(math.radians(theta))
def polarToY(r:float, theta:float)->float:
    return r*math.sin(math.radians(theta))