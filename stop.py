from lidarLib.Lidar import Lidar

lidar = Lidar()
lidar.connect(port="/dev/lidar1", baudrate=256000, timeout=3)

lidar.stop()
lidar.disconnect()

