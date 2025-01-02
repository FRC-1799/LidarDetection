import math

def polarToCart(r,theta):
    return polarToX(r, theta), polarToY(r, theta)

def cartToPolar(x, y):
    return math.sqrt(x**2+ y**2), math.atan2(y,x)

def polarToX(r, theta):
    return r*math.cos(math.radians(theta))
def polarToY(r, theta):
    return r*math.sin(math.radians(theta))