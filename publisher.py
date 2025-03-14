import ntcore
from wpimath.geometry import Pose2d, Rotation2d

from constants import constants
from lidarHitboxingMap import lidarHitboxMap
from lidarLib.lidarMeasurment import lidarMeasurement
from lidarHitboxNode import lidarHiboxNode
from lidarLib.translation import translation


class publisher:
    def __init__ (self):
        self.inst:ntcore.NetworkTableInstance = ntcore.NetworkTableInstance.getDefault()
        #self.inst.setServerTeam(1799)
        
        self.inst.setServer("127.0.0.1")
        #self.inst.startServer()
        self.inst.startClient4("lidar")
        


        self.publishFolder=  self.inst.getTable("lidar")
        self.individualPointTopic = self.publishFolder.getStructArrayTopic("individualReadings", Pose2d)
        self.individualPointPublisher = self.individualPointTopic.publish()

        self.hitboxTopic = self.publishFolder.getStructArrayTopic("detectedHitboxes", Pose2d)
        self.hitboxPublisher = self.hitboxTopic.publish()

        self.poseTopic = self.inst.getStructTopic("robotPose", Pose2d)
        self.poseSubscriber = self.poseTopic.subscribe(Pose2d())
        

        self.nodeWidthTopic = self.publishFolder.getFloatTopic("NodeWidth")
        self.nodeWidthPublisher = self.nodeWidthTopic.publish()
        self.nodeWidthPublisher.set(constants.mapNodeSizeMeters)

        self.lidarPoseTopic = self.publishFolder.getStructArrayTopic("lidarPoses", Pose2d)
        self.lidarPosePublisher = self.lidarPoseTopic.publish()

        print ("publisher is up and running")
        print(self.inst.getNetworkMode())
        



    def getPose(self):
        return self.poseSubscriber.get()
    
    def publishPointsFromPoses(self, poses:list[Pose2d]):
        
        self.individualPointPublisher.set(poses)
    translation.fromCart(5000,5000,0)
    def publishPointsFromLidarMeasurments(self, measurments:list[lidarMeasurement]):
        poses:list[Pose2d] = []
        for measurment in measurments:
            poses.append(Pose2d(measurment.getX()/1000, measurment.getY()/1000, Rotation2d()))

        self.publishPointsFromPoses(poses)

    def publishHiboxesFromPoses(self, poses:list[Pose2d]):
        print("data sent   ", self.inst.isConnected())
        self.hitboxPublisher.set(poses)
        

    def publishHitboxesFromHitboxMap(self, map:lidarHitboxMap):
        poses:list[Pose2d] = []
        for node in map.getAs1DList():
            node:lidarHiboxNode
            if (not node.isOpen):
                poses.append(Pose2d(node.x, node.y, Rotation2d()))
        
        self.publishHiboxesFromPoses(poses)

    def updateNodeWith(self, nodeWidth:int):
        self.nodeWidthPublisher.set(nodeWidth)


    def publishLidarPosesFromPose(self, poses:Pose2d):
        self.lidarPosePublisher.set(poses)

    def publishLidarPosesFromTrans(self, trans:list[translation]):
        poses:Pose2d = []
        for translation in trans:
            poses.append(Pose2d(translation.x/1000, translation.y/1000, translation.rotation))

        self.publishLidarPosesFromPose(poses)

    def isConnected(self)->bool:
        return self.inst.isConnected()