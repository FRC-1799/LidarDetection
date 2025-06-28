from lidarLib.LidarConfigs import lidarConfigs
from lidarLib import LidarConfigs


config:lidarConfigs = lidarConfigs("test")

config.writeToJson("test.json")

config = lidarConfigs.configsFromJson("test.json")
config.printConfigs()