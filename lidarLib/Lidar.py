
from time import sleep
from lidarLib.pyrplidarSerial import PyRPlidarSerial
from lidarLib.lidarProtocol import *
import lidarLib.lidarProtocol
from lidarLib.lidarMap import lidarMap
from lidarLib.lidarMeasurment import lidarMeasurement
import threading
from lidarLib.translation import translation


class Lidar:

    def __init__(self, debugMode=False, deadband=None):
        self.lidarSerial = None
        self.measurements = None
        self.currentMap=lidarMap(self)
        self.lastMap=lidarMap(self)
        #self.eventLoop()
        self.deadband=deadband
        self.capsuleType=None
        self.loop = None
        self.dataDiscriptor=None
        self.isDone=False
        self.currentMotorPWM=0
        self.debugMode=debugMode

        self.localTranslation=translation.default()
        self.globalTranslation=translation.default()
        self.combinedTranslation=translation.default()

        
        

    
    def __del__(self):
        
        self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exceptionType, exceptionValue, exceptionTraceback):
        self.disconnect()

    def connect(self, port="/dev/ttyUSB0", baudrate=115200, timeout=3)->None:
        self.lidarSerial = PyRPlidarSerial()
        self.lidarSerial.open(port, baudrate, timeout)
        
        if self.lidarSerial.isOpen():
            print("PyRPlidar Info : device is connected")
        else:
            self.readToCapsule=None
            raise ConnectionError("could not find lidar unit")
        



    def establishLoop(self, updateFunc:function,resetLoop=True)->None:
        self.update=updateFunc
        self.dataDiscriptor = self.receiveDiscriptor()
        if resetLoop:
            self.loop = threading.Thread(target=self.updateLoop, daemon=False)
            self.loop.start()

    def disconnect(self, leaveRunning=False)->None:
        
        if self.lidarSerial is not None:
            self.isDone=True
            if not leaveRunning:
                self.stop()
                self.setMotorPwm(0)
            self.lidarSerial.close()
            
            self.lidarSerial = None
            print("PyRPlidar Info : device is disconnected")

    def updateLoop(self)->None:
        while not self.isDone:
            self.update()
            sleep(0.001)
            
    def restartScan(self)->None:
        self.stop()
        #self.setMotorPwm(0)
        
        #sleep(0.001)
        self.lidarSerial.flush()
        
        
        self.startRawScan()
        


    def update(self)->None:
        
        raise PyRPlidarProtocolError("Update was called without a valid connection established, this may because a user tried to call it")


    def standardUpdate(self)->None:
        
        while not self.isDone:
            #print(self.lidarSerial.bufferSize())
            if self.dataDiscriptor and (self.lidarSerial.bufferSize()>=self.dataDiscriptor.data_length):
                #print("update working")
                newData=self.receiveData(self.dataDiscriptor)
                if not self.validatePackage(newData, printErrors=self.debugMode):
                    self.restartScan()
                    return
                self.currentMap.addVal(lidarMeasurement(newData), self.combinedTranslation, printFlag=self.debugMode)
            else:
                #print("break hit")
                break
        
        #print("thingy")

    def capsuleUpdate(self)->None:
        data = self.receiveData(self.dataDiscriptor)
        capsule_prev = self.capsuleType(data)
        capsule_current = None
        
        while not self.isDone:
            print("update")
            if self.dataDiscriptor and (self.lidarSerial.bufferSize()>=self.dataDiscriptor.data_length):
                print("data read")
                data = self.receiveData(self.dataDiscriptor)
                capsule_current = self.capsuleType(data)
                
                nodes = self.capsuleType._parse_capsule(capsule_prev, capsule_current)
                for index, node in enumerate(nodes):
                        self.currentMap.addVal(lidarMeasurement(raw_bytes=None, measurement_hq=node), self.combinedTranslation, printFlag=True)

                capsule_prev = capsule_current
            else:
                return


    def validatePackage(self, pack:bytes, printErrors=False)->bool:
        startFlag = bool(pack[0] & 0x1)
        quality = pack[0] >> 2
        angle = ((pack[1] >> 1) + (pack[2] << 7)) / 64.0
        distance = (pack[3] + (pack[4] << 8)) / 4.0


        #checks first checksum
        if startFlag == bool(pack[0]>>1 & 0x1):
            if printErrors:
                print("Start flag checksum was invalid")
            return False
        
        #checks second checksum
        if not bool(pack[1]&0x1):
            if printErrors:
                print("second byte checksum was invalid")
            return False

        #checks if angle is over 360
        if angle>360:
            if printErrors:
                print("angle was invalid at value ", angle)
            return False
        
        #checks if distance is over 25 meters(max for lidar should be 16)
        if distance>25000:
            if printErrors:
                print("distance was too far away to be legit at value ", distance)
            return False

        return True
        


    def sendCommand(self, cmd:bytes, payload=None)->None:
        if self.lidarSerial == None:
            raise PyRPlidarConnectionError("PyRPlidar Error : device is not connected")

        self.lidarSerial.send_data(PyRPlidarCommand(cmd, payload).raw_bytes)

    def receiveDiscriptor(self)->PyRPlidarResponse:
        if self.lidarSerial == None:
            raise PyRPlidarConnectionError("PyRPlidar Error : device is not connected")
        
        discriptor = PyRPlidarResponse(self.lidarSerial.receive_data(RPLIDAR_DESCRIPTOR_LEN))
        
        if discriptor.sync_byte1 != RPLIDAR_SYNC_BYTE1[0] or discriptor.sync_byte2 != RPLIDAR_SYNC_BYTE2[0]:
            raise PyRPlidarProtocolError("PyRPlidar Error : sync bytes are mismatched", hex(discriptor.sync_byte1), hex(discriptor.sync_byte2))
        return discriptor

    def receiveData(self, discriptor:PyRPlidarResponse)->bytes:
        
        if self.lidarSerial == None:
            raise PyRPlidarConnectionError("PyRPlidar Error : device is not connected")
        
        data = self.lidarSerial.receive_data(discriptor.data_length)
        if len(data) != discriptor.data_length:
            raise PyRPlidarProtocolError()
        return data



    def stop(self)->None:
        self.sendCommand(RPLIDAR_CMD_STOP)

    def reset(self)->None:
        self.sendCommand(RPLIDAR_CMD_RESET)

    def setMotorPwm(self, pwm:int, overrideInternalValue=True)->None:
        if pwm<0 or pwm>RPLIDAR_MAX_MOTOR_PWM:
            raise ValueError("lidar pwm was set to a value not within the range: ",pwm)
        self.lidarSerial.set_dtr(False)
        self.sendCommand(RPLIDAR_CMD_SET_MOTOR_PWM, struct.pack("<H", pwm))
        if overrideInternalValue:
            self.currentMotorPWM=pwm
    
    

    def getInfo(self)->PyRPlidarDeviceInfo:
        self.sendCommand(RPLIDAR_CMD_GET_INFO)
        discriptor = self.receiveDiscriptor()
        data = self.receiveData(discriptor)
        return PyRPlidarDeviceInfo(data)

    def getHealth(self)->PyRPlidarHealth:
        self.sendCommand(RPLIDAR_CMD_GET_HEALTH)
        discriptor = self.receiveDiscriptor()
        data = self.receiveData(discriptor)
        return PyRPlidarHealth(data)

    def getSampleRate(self)->PyRPlidarSamplerate:
        self.sendCommand(RPLIDAR_CMD_GET_SAMPLERATE)
        discriptor = self.receiveDiscriptor()
        data = self.receiveData(discriptor)
        return PyRPlidarSamplerate(data)

    def getLidarConf(self, payload:struct)->bytes:
        self.sendCommand(RPLIDAR_CMD_GET_LIDAR_CONF, payload)
        discriptor = self.receiveDiscriptor()
        data = self.receiveData(discriptor)
        return data

    def get_scan_mode_count(self)->int:
        data = self.getLidarConf(struct.pack("<I", RPLIDAR_CONF_SCAN_MODE_COUNT))
        count = struct.unpack("<H", data[4:6])[0]
        return count

    def getScanModeTypical(self)->int:
        data = self.getLidarConf(struct.pack("<I", RPLIDAR_CONF_SCAN_MODE_TYPICAL))
        typical_mode = struct.unpack("<H", data[4:6])[0]
        return typical_mode

    def getScanModes(self)->list[bytes]:
        
        scan_modes = []
        scan_mode_count = self.get_scan_mode_count()
        
        for mode in range(scan_mode_count):
            scan_mode = PyRPlidarScanMode(
                            self.getLidarConf(struct.pack("<IH", RPLIDAR_CONF_SCAN_MODE_NAME, mode)),
                            self.getLidarConf(struct.pack("<IH", RPLIDAR_CONF_SCAN_MODE_MAX_DISTANCE, mode)),
                            self.getLidarConf(struct.pack("<IH", RPLIDAR_CONF_SCAN_MODE_US_PER_SAMPLE, mode)),
                            self.getLidarConf(struct.pack("<IH", RPLIDAR_CONF_SCAN_MODE_ANS_TYPE, mode)))
            print(scan_mode)
            scan_modes.append(scan_mode)
        
        return scan_modes


    def startScan(self)->None:
        
        self.sendCommand(RPLIDAR_CMD_SCAN)
        #self.setMotorPwm(self.currentMotorPWM)
        
        self.establishLoop(self.standardUpdate)



    def startRawScan(self)->None:
        self.sendCommand(RPLIDAR_CMD_SCAN)
        self.lidarSerial.receive_data(RPLIDAR_DESCRIPTOR_LEN)
    
    @DeprecationWarning
    def startScanExpress(self, mode:int):
        
        self.sendCommand(RPLIDAR_CMD_EXPRESS_SCAN, struct.pack("<BI", mode, 0x00000000))
        self.establishLoop(self.capsuleUpdate)

        if self.dataDiscriptor.data_type == 0x82:
            self.capsuleType = PyRPlidarScanCapsule
        elif self.dataDiscriptor.data_type == 0x84:
            self.capsuleType = PyRPlidarScanUltraCapsule
        elif self.dataDiscriptor.data_type == 0x85:
            self.capsuleType = PyRPlidarScanDenseCapsule
        else:
            raise PyRPlidarProtocolError("RPlidar Error : scan data type is not supported")
        

            

        

    
    def forceScan(self)->None:
        self.sendCommand(RPLIDAR_CMD_FORCE_SCAN)
        self.establishLoop(self.standardUpdate)

    
    def mapIsDone(self)->None:
        
        self.lastMap=self.currentMap
        self.currentMap=lidarMap(self, mapID=self.lastMap.mapID+1, deadband=self.deadband, sensorThetaOffset=self.localTranslation.theta)
        if self.debugMode:
            print("map swap attempted")
            print(len(self.lastMap.getPoints()),self.lastMap.len, self.lastMap.mapID, self.lastMap.getRange(), self.lastMap.getHz(), self.lastMap.getPeriod())
            print(len(self.currentMap.getPoints()),self.currentMap.len ,self.currentMap.mapID)
        
        #print(self.currentMap.points==self.lastMap.points)

    def getCurrentMap(self)->lidarMap:
        return self.currentMap

    def setCurrentLocalTranslation(self, translation:translation)->None:
        self.localTranslation=translation
        self.currentMap.setOffset(self.localTranslation.theta)
        self.combinedTranslation=self.localTranslation.combineTranslation(self.globalTranslation)

    def setCurrentGlobalTranslation(self, translation:translation)->None:
        self.globalTranslation=translation
        self.combinedTranslation=self.globalTranslation.combineTranslation(self.localTranslation)


    def setDeadband(self, deadband:list[int])->None:
        self.deadband=deadband
        self.currentMap.setDeadband(deadband)