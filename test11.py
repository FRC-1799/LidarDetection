import os
from math import floor
from adafruit_rplidar import RPLidar


# Setup the RPLidar
PORT_NAME = '/dev/lidar1'
lidar = RPLidar(None, PORT_NAME, timeout=3, baudrate=256000)

# used to scale data to fit on the screen
max_distance = 0

def process_data(data):
    print(data, '\n')

scan_data = [0]*360

try:
#    print(lidar.get_info())
    for scan in lidar.iter_measurements(scan_type=2):
        print(scan)
        # for (_, angle, distance) in scan:
        #     scan_data[min([359, floor(angle)])] = distance
        # process_data(scan_data)

except KeyboardInterrupt:
    print('Stopping.')
lidar.stop()
lidar.disconnect()