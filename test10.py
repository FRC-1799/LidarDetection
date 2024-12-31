import os
from math import floor
from adafruit_rplidar import RPLidar
import matplotlib.animation as animation
from functools import partial
import numpy as np
import time
import matplotlib.pyplot as plot

# Setup the RPLidar
PORT_NAME = '/dev/lidar1'
lidar = RPLidar(None, PORT_NAME, timeout=3, baudrate=256000, logging=True)

# used to scale data to fit on the screen
max_distance = 0

def process_data(data):
    print(data, '\n')

def update_line(num, lidar, subplot):
    scan = next(lidar.iter_scans(max_buf_meas=100000))

    angles=np.array([point[1] for point in scan])
    distances=np.array([point[2] for point in scan])
    #offsets = np.array([[point.angle, point.distance] for point in scan])
    #offsets=[scan[0].angle, scan[0].distance]
    #subplot.set_offsets(offsets)
    intens = np.array([point[0] for point in scan])
    #subplot.set_array(intens)
    print("render cycle", len(intens))
    return subplot.scatter(angles*3.14/180, distances, s=10, c=intens, cmap=plot.cm.Greys_r, lw=0),





#scan_data = [0]*360
fig = plot.figure()
subplot = plot.subplot(111, projection='polar')
# axis = subplot.scatter([0, 1], [100, 2000], s=1, c=[IMIN, IMAX],
#                        cmap=plot.cm.Greys_r, lw=0)
subplot.set_rmax(4000)
subplot.grid(True)

time.sleep(1)
print("hello")
#lidar.currentMap.printMap()
#print(lidar.currentMap.points)
#lidar.currentMap.thisFuncDoesNothing()

# anim=animation.FuncAnimation(fig, update_line,
#     fargs=(lidar, subplot), interval=50, save_count=50)
while True:
    print(next(lidar.iter_scans(max_buf_meas=100000)))
# ani = animation.FuncAnimation(
# fig, partial(update_line, lidar=lidar, line=line),
#frames=np.linspace(0, 2*np.pi, 128), blit=True)
#plot.show()

#    print(lidar.get_info())

    # for (_, angle, distance) in scan:
    #     scan_data[min([359, floor(angle)])] = distance
    # process_data(scan_data)

print("cehckout")
lidar.stop()
lidar.disconnect()