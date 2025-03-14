import ntcore
from wpimath.geometry import Pose2d, Rotation2d

from constants import constants
from lidarHitboxingMap import lidarHitboxMap
from lidarLib.lidarMeasurment import lidarMeasurement
from lidarHitboxNode import lidarHiboxNode


class publisher:
    def __init__ (self):
        self.inst:ntcore.NetworkTableInstance = ntcore.NetworkTablesInstance.getDefault()
        self.inst.setServerTeam(1799)
        self.inst.startClient4("lidar")
        


        self.publishFolder=  self.inst.getTable("lidar")
        self.individualPointTopic = self.publishFolder.getStructArrayTopic("individualReadings", Pose2d)
        self.individualPointPublisher = self.individualPointTopic.publish()

        self.hitboxTopic = self.publishFolder.getStructTopic("detectedHitboxes", Pose2d)
        self.hitboxPublisher = self.hitboxTopic.publish()

        self.poseTopic = self.inst.getStructTopic("robotPose", Pose2d)
        self.poseSubscriber = self.poseTopic.subscribe(Pose2d())
        

        self.nodeWidthTopic = self.publishFolder.getFloatTopic("NodeWidth")
        self.nodeWidthPublisher = self.nodeWidthTopic.publish()
        self.nodeWidthPublisher.set(constants.mapNodeSizeMeters)



    def getPose(self):
        return self.poseSubscriber.get()
    
    def publishPointsFromPoses(self, poses:list[Pose2d]):
        
        self.individualPointPublisher.set(poses)
    
    def publishPointsFromLidarMeasurments(self, measurments:list[lidarMeasurement]):
        poses:list[Pose2d] = []
        for measurment in measurments:
            poses.append(Pose2d(measurment.getX(), measurment.getY(), Rotation2d()))

        self.publishPointsFromPoses(poses)

    def publishHiboxesFromPoses(self, poses:list[Pose2d]):
        self.hitboxPublisher.set(poses)
        self.publishFolder.flush()

    def publishHitboxesFromHitboxMap(self, map:lidarHitboxMap):
        poses:list[Pose2d] = []
        for node in lidarHitboxMap.getAs1DList():
            node:lidarHiboxNode
            if (not node.isOpen):
                poses.append(Pose2d(node.getX(), node.getY(), Rotation2d()))
        
        self.publishHiboxesFromPoses(poses)

    def updateNodeWith(self, nodeWidth:int):
        self.nodeWidthPublisher.set(nodeWidth)


