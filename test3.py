#!/usr/bin/env python3
'''Animates distances and measurment quality'''
from lidarLib.lidar import lidar
import matplotlib.pyplot as plot
import numpy as np
import matplotlib.animation as animation
import time

PORT_NAME = '/dev/ttyUSB0'
DMAX = 4000
IMIN = 0
IMAX = 20

def update_line(num, iterator, line):
    scan = next(iterator)
    offsets = np.array([scan.angle*3.14/180, scan.distance])
    line.set_offsets(offsets)
    intens = np.array([meas[0] for meas in scan])
    line.set_array(intens)
    return line,

def run():
    lidar = lidar()
    lidar.connect(port="/dev/ttyUSB0", baudrate=256000, timeout=3)
    lidar.set_motor_pwm(500)
    time.sleep(2)
    fig = plot.figure()
    axis = plot.subplot(111, projection='polar')
    line = axis.scatter([0, 0], [0, 0], s=5, c=[IMIN, IMAX],
                           cmap=plot.cm.Greys_r, lw=0)
    axis.set_rmax(DMAX)
    axis.grid(True)
    scan_generator = lidar.force_scan()

    iterator = scan_generator()
    anim=animation.FuncAnimation(fig, update_line,
        fargs=(iterator, line), interval=50, save_count=50)
    plot.show()
    lidar.stop()
    lidar.set_motor_pwm(0)
    lidar.disconnect()
    print("the run is done")

if __name__ == '__main__':
    run()