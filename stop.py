from lidarLib.Lidar import Lidar
import sys

from lidarLib.LidarConfigs import lidarConfigs

def stop(port:str):
    lidar = Lidar(lidarConfigs(port))
    lidar.connect()

    lidar.stop()
    lidar.disconnect()

if __name__ == '__main__':
    if len(sys.argv)>1:
        stop(sys.argv[1])
    else:
        stop("/dev/lidar0")