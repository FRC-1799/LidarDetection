#!/usr/bin/env python3
'''Animates distances and measurment quality'''
from lidarLib.Lidar import Lidar
import matplotlib.pyplot as plot
import numpy as np
import matplotlib.animation as animation
from functools import partial
import time

PORT_NAME = '/dev/ttyUSB0'
DMAX = 1600
IMIN = 20
IMAX = 20

def update_line(num, lidar, subplot):
    scan = lidar.lastMap.getPoints()

    angles=np.array([point.angle for point in scan])
    distances=np.array([point.distance for point in scan])
    #offsets = np.array([[point.angle, point.distance] for point in scan])
    #offsets=[scan[0].angle, scan[0].distance]
    #subplot.set_offsets(offsets)
    intens = np.array([point.quality for point in scan])
    #subplot.set_array(intens)
    print("render cycle", len(intens))
    return subplot.scatter(angles*3.14/180, distances, s=10, c=intens, cmap=plot.cm.Greys_r, lw=0),

def run():
    lidar = Lidar()
    lidar.connect(port="/dev/lidar1", baudrate=256000, timeout=3)
    lidar.setMotorPwm(200)
    
    lidar.getScanModes()
    print(lidar.getSampleRate())
    print(lidar.getScanModeTypical())
    #lidar.startScanExpress(3)
    lidar.startScan()
    time.sleep(2)
    fig = plot.figure()
    subplot = plot.subplot(111, projection='polar')
    # axis = subplot.scatter([0, 1], [100, 2000], s=1, c=[IMIN, IMAX],
    #                        cmap=plot.cm.Greys_r, lw=0)
    subplot.set_rmax(DMAX)
    subplot.grid(True)
    
    time.sleep(1)
    #lidar.currentMap.printMap()
    #print(lidar.currentMap.points)
    #lidar.currentMap.thisFuncDoesNothing()

    
    anim=animation.FuncAnimation(fig, update_line,
        fargs=(lidar, subplot), interval=50, save_count=50)
    # ani = animation.FuncAnimation(
    # fig, partial(update_line, lidar=lidar, line=line),
    #frames=np.linspace(0, 2*np.pi, 128), blit=True)
    plot.show()
    
    lidar.stop()
    
    lidar.disconnect()
    
    print("the run is done")

if __name__ == '__main__':
    run()