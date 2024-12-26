#!/usr/bin/env python3
'''Animates distances and measurment quality'''
from lidarLib.Lidar import Lidar
import matplotlib.pyplot as plot
import numpy as np
import matplotlib.animation as animation
from functools import partial
import time

PORT_NAME = '/dev/ttyUSB0'
DMAX = 4000
IMIN = 20
IMAX = 20

def update_line(num, lidar, line):
    scan = lidar.currentMap.getPoints()
    offsets = np.array([[point.angle*3.14/180, point.distance] for point in scan])
    #offsets=[scan[0].angle, scan[0].distance]
    line.set_offsets(offsets)
    intens = np.array([point.quality for point in scan])
    line.set_array(intens)
    return line,

def run():
    lidar = Lidar()
    lidar.connect(port="/dev/lidar1", baudrate=256000, timeout=3)
    lidar.set_motor_pwm(1000)
    time.sleep(2)
    fig = plot.figure()
    axis = plot.subplot(111, projection='polar')
    line = axis.scatter([0, 1], [100, 2000], s=1, c=[IMIN, IMAX],
                           cmap=plot.cm.Greys_r, lw=0)
    axis.set_rmax(DMAX)
    axis.grid(True)
    lidar.startScanExpress(4)
    time.sleep(1)
    #lidar.currentMap.printMap()
    #print(lidar.currentMap.points)
    #lidar.currentMap.thisFuncDoesNothing()

    
    anim=animation.FuncAnimation(fig, update_line,
        fargs=(lidar, line), interval=50, save_count=50)
    # ani = animation.FuncAnimation(
    # fig, partial(update_line, lidar=lidar, line=line),
    #frames=np.linspace(0, 2*np.pi, 128), blit=True)
    plot.show()
    
    lidar.stop()
    lidar.set_motor_pwm(0)
    lidar.disconnect()
    
    print("the run is done")

if __name__ == '__main__':
    run()