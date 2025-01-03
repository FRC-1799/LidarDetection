import math

def polarToCart(r,theta):
    return polarToX(r, theta), polarToY(r, theta)

def cartToPolar(x, y):
    deg=math.degrees(math.atan2(y,x))
    if deg<0:
        deg+=360
    return math.sqrt(x**2+ y**2), deg

def polarToX(r, theta):
    return r*math.cos(math.radians(theta))
def polarToY(r, theta):
    return r*math.sin(math.radians(theta))