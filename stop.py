from lidarLib.Lidar import Lidar
import sys

def stop(port:str):
    lidar = Lidar()
    lidar.connect(port=port, baudrate=256000, timeout=3)

    lidar.stop()
    lidar.disconnect()

if __name__ == '__main__':
    if len(sys.argv)>1:
        stop(sys.argv[1])
    else:
        stop("/dev/lidar0")