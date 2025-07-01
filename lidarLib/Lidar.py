
from time import sleep
from lidarLib.LidarConfigs import lidarConfigs
from lidarLib.rplidarSerial import RPlidarSerial
from lidarLib.lidarProtocol import *
import lidarLib.lidarProtocol
from lidarLib.lidarMap import lidarMap
from lidarLib.lidarMeasurment import lidarMeasurement
import threading
from lidarLib.translation import translation
from typing import Callable


class Lidar:
    """class to handle, read, and translate data from a RPlidar (only A2M12 has been tested but should work for all)"""
    def __init__(self, config:lidarConfigs):
        """initalizes lidar object but does not attempt to connect or start any scans"""
        self.lidarSerial = None
        self.measurements = None
        self.currentMap=lidarMap(self)
        self.lastMap=lidarMap(self)
        #self.eventLoop()
        #self.deadband=deadband
        self.config = config
        self.capsuleType=None
        self.loop = None
        self.dataDiscriptor=None
        self.isDone=False
        self.currentMotorPWM=0
        #self.debugMode=debugMode



        self.localTranslation=self.config.localTrans
        self.globalTranslation=translation.default()
        self.combinedTranslation=translation.default()
        

        
        

    
    def __del__(self):
        
        self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exceptionType, exceptionValue, exceptionTraceback):
        self.disconnect()

    def connect(self)->None:
        """Connects lidar object to the spesified port with the specified baud rate but does not check to make sure the port specified contains a lidar. """
        self.lidarSerial = RPlidarSerial()
        self.lidarSerial.open(self.config.port, self.config.baudrate,timeout=self.config.timeout)
        print(self.config.port)
        print(self.config.baudrate)
        
        if self.lidarSerial.isOpen():
            print("PyRPlidar Info : device is connected")
        else:
            self.readToCapsule=None
            raise ConnectionError("could not find lidar unit")
        
        if self.config.autoStart:
            if self.config.mode=="normal":
                self.startScan()
        

    def isRunning(self):
        return self.loop and self.loop.is_alive()

    def __establishLoop(self, updateFunc:Callable,resetLoop=True)->None:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            Establishes the update loop thread as well as fetching a scan descriptor
            if reset loop is set to false the function will only fetch the discriptor and change the update function but it will not tamper with the update thread
        """
        self.__update=updateFunc
        self.dataDiscriptor = self.__receiveDiscriptor()
        if resetLoop:
            self.loop = threading.Thread(target=self.__updateLoop, daemon=True)
            self.loop.start()

    def disconnect(self, leaveRunning=False)->None:
        """
            Disconects the lidar from a connected port
            Before disconecting the function will stop the lidar motor and scan(if aplicable) unless leaveRunning is set to true
        """
        if self.lidarSerial is not None:
            self.isDone=True
            if not leaveRunning:
                self.stop()
                self.setMotorPwm(0)
            self.lidarSerial.close()
            
            self.lidarSerial = None
            print("PyRPlidar Info : device is disconnected")

    def __updateLoop(self)->None:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            function called by the update loop so that the actual update function can be changed depending on the scan type run
        """
        while not self.isDone:
            self.__update()
            sleep(0.001)
            
    def restartScan(self)->None:
        """Restarts the running scan, this function only works for simple scans rn and calling it during any other scan type may cause issues"""
        self.stop()
        #self.setMotorPwm(0)
        
        #sleep(0.001)
        self.lidarSerial.flush()
        
        
        self.__startRawScan()
        


    def __update(self)->None:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            placeholder function, update is revalued whenever a scan is started so this code should never run. for more information see __standardUpdate or __expressUpdate
        """
        raise RPlidarProtocolError("Update was called without a valid connection established, this may because a user tried to call it")


    def __standardUpdate(self)->None:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            actual update function for standard and force scans. Will read the buffer into new measurments which are passed into the current map
        """
        
        while not self.isDone:
            #print(self.lidarSerial.bufferSize())
            if self.dataDiscriptor and (self.lidarSerial.bufferSize()>=self.dataDiscriptor.data_length):
                #print("update working")
                newData=self.__receiveData(self.dataDiscriptor)
                if not self.validatePackage(newData, printErrors=self.config.debugMode):
                    self.restartScan()
                    return
                self.currentMap.addVal(lidarMeasurement(newData), self.combinedTranslation, printFlag=self.config.debugMode)
            else:
                #print("break hit")
                break
        
        #print("thingy")
    @DeprecationWarning
    def __capsuleUpdate(self)->None:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            DEPRECATED
            actual update function for express scans. Will read the buffer into new measurments which are passed into the current map
            since the express scan is currently deprecated in this library this function should never be called
        """
        data = self.__receiveData(self.dataDiscriptor)
        capsule_prev = self.capsuleType(data)
        capsule_current = None
        
        while not self.isDone:
            print("update")
            if self.dataDiscriptor and (self.lidarSerial.bufferSize()>=self.dataDiscriptor.data_length):
                print("data read")
                data = self.__receiveData(self.dataDiscriptor)
                capsule_current = self.capsuleType(data)
                
                nodes = self.capsuleType._parse_capsule(capsule_prev, capsule_current)
                for index, node in enumerate(nodes):
                        self.currentMap.addVal(lidarMeasurement(raw_bytes=None, measurement_hq=node), self.combinedTranslation, printFlag=True)

                capsule_prev = capsule_current
            else:
                return


    def validatePackage(self, pack:bytes, printErrors=False)->bool:
        """Takes a 5 lenght byte pack responce to a standard or forced scan and returns wether or not that scan has all of the correct checksums(and some other checks for legitimacy)"""
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
        


    def __sendCommand(self, cmd:bytes, payload=None)->None:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            sends the specified command over the serial bus. throws an RPlidarConnectionError if no serial bus is connected
        """
        if self.lidarSerial == None:
            raise RPlidarConnectionError("PyRPlidar Error : device is not connected")

        self.lidarSerial.sendData(RPlidarCommand(cmd, payload).raw_bytes)

    def __receiveDiscriptor(self)->RPlidarResponse:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            Recives but does not save a rplidar scan descriptor. Assumes that the discriptor is the first thing in the bus and will otherwise throw an error
        """
        if self.lidarSerial == None:
            raise RPlidarConnectionError("PyRPlidar Error : device is not connected")
        
        discriptor = RPlidarResponse(self.lidarSerial.receiveData(RPLIDAR_DESCRIPTOR_LEN))
        
        if discriptor.sync_byte1 != RPLIDAR_SYNC_BYTE1[0] or discriptor.sync_byte2 != RPLIDAR_SYNC_BYTE2[0]:
            raise RPlidarProtocolError("PyRPlidar Error : sync bytes are mismatched", hex(discriptor.sync_byte1), hex(discriptor.sync_byte2))
        return discriptor

    def __receiveData(self, discriptor:RPlidarResponse)->bytes:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            fetches a package from the lidar using the entered discriptor as a guide
        """
        if self.lidarSerial == None:
            raise RPlidarConnectionError("PyRPlidar Error : device is not connected")
        
        data = self.lidarSerial.receiveData(discriptor.data_length)
        if len(data) != discriptor.data_length:
            raise RPlidarProtocolError()
        return data



    def stop(self)->None:
        """Stops the current scan cycle on the lidar but does not stop the motor"""
        self.__sendCommand(RPLIDAR_CMD_STOP)

    def reset(self)->None:
        """Restarts the lidar as if it was just powered on but does not effect the cliant side lidar lib at all"""
        self.__sendCommand(RPLIDAR_CMD_RESET)

    def setMotorPwm(self, pwm:int=0, overrideInternalValue=True)->None:
        """Sets the lidars motor to the specified pwm value. the speed must be a positive number or 0 and lower or equal to the specified max value(currently 1023)"""
        if pwm<0 or pwm>RPLIDAR_MAX_MOTOR_PWM:
            raise ValueError("lidar pwm was set to a value not within the range: ",pwm)
        self.lidarSerial.setDtr(False)

        if self.config.defaultSpeed<0 or self.config.defaultSpeed>RPLIDAR_MAX_MOTOR_PWM:
            raise ValueError("lidar config pwm was set to a value not within the range: ",pwm)


        if overrideInternalValue:
            self.config.defaultSpeed=pwm

        self.__sendCommand(RPLIDAR_CMD_SET_MOTOR_PWM, struct.pack("<H", self.config.defaultSpeed))
        
    
    

    def getInfo(self)->RPlidarDeviceInfo:
        """Fetches and returns the connected lidars info in the form of a RPlidarDeviceInfo object"""
        self.__sendCommand(RPLIDAR_CMD_GET_INFO)
        discriptor = self.__receiveDiscriptor()
        data = self.__receiveData(discriptor)
        return RPlidarDeviceInfo(data)

    def getHealth(self)->RPlidarHealth:
        """Fetches and returns the connected lidars health in the form of a RPlidarDeviceHealth object"""
        self.__sendCommand(RPLIDAR_CMD_GET_HEALTH)
        discriptor = self.__receiveDiscriptor()
        data = self.__receiveData(discriptor)
        return RPlidarHealth(data)

    def getSampleRate(self)->RPlidarSamplerate:
        """
            Fetches and returns the connected lidars sample rates for both standard and express modes. 
            The measurments are in microseconds per reading. the data is returned in the form of a RPlidarSamplerateObject.
        """
        self.__sendCommand(RPLIDAR_CMD_GET_SAMPLERATE)
        discriptor = self.__receiveDiscriptor()
        data = self.__receiveData(discriptor)
        return RPlidarSamplerate(data)

    def __getLidarConf(self, payload:struct)->bytes:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            Fetches and returns the connected lidars current configuration and returns it as a pack of bytes
        """
        self.__sendCommand(RPLIDAR_CMD_GET_LIDAR_CONF, payload)
        discriptor = self.__receiveDiscriptor()
        data = self.__receiveData(discriptor)
        return data

    def getScanModeCount(self)->int:
        """Fetches and returns the number of scan modes supported by the connected lidar"""
        data = self.__getLidarConf(struct.pack("<I", RPLIDAR_CONF_SCAN_MODE_COUNT))
        count = struct.unpack("<H", data[4:6])[0]
        return count

    def getScanModeTypical(self)->int:
        """Fetches and returns the best scan mode fot the connected lidar"""
        data = self.__getLidarConf(struct.pack("<I", RPLIDAR_CONF_SCAN_MODE_TYPICAL))
        typical_mode = struct.unpack("<H", data[4:6])[0]
        return typical_mode

    def getScanModes(self)->list[RPlidarScanMode]:
        """
            fetches and returns a list of RPlidarScanMode objects for each scan mode supported by the current connected lidar.
            WARNING: some of the modes returned may be supported by the lidar but not supported by the cliant side lib.
        """
        scan_modes = []
        scan_mode_count = self.getScanModeCount()
        
        for mode in range(scan_mode_count):
            scan_mode = RPlidarScanMode(
                            self.__getLidarConf(struct.pack("<IH", RPLIDAR_CONF_SCAN_MODE_NAME, mode)),
                            self.__getLidarConf(struct.pack("<IH", RPLIDAR_CONF_SCAN_MODE_MAX_DISTANCE, mode)),
                            self.__getLidarConf(struct.pack("<IH", RPLIDAR_CONF_SCAN_MODE_US_PER_SAMPLE, mode)),
                            self.__getLidarConf(struct.pack("<IH", RPLIDAR_CONF_SCAN_MODE_ANS_TYPE, mode)))
            #print(scan_mode)
            scan_modes.append(scan_mode)
        
        return scan_modes


    def startScan(self)->None:
        """Starts a standard scan on the lidar and starts the update cycle"""
        
        self.__sendCommand(RPLIDAR_CMD_SCAN)
        self.setMotorPwm(overrideInternalValue=False)
        
        self.__establishLoop(self.__standardUpdate)



    def __startRawScan(self)->None:
        """
            INTERNAL FUNCTION, NOT FOR OUTSIDE USE
            Initalizes a scan without starting a even loop or resaving discriptor information. If both of those things have not already been started/saved calling this function will lead to issues
        """
        self.__sendCommand(RPLIDAR_CMD_SCAN)
        self.lidarSerial.receiveData(RPLIDAR_DESCRIPTOR_LEN)
    

    @DeprecationWarning
    def startScanExpress(self, mode:int):
        
        self.__sendCommand(RPLIDAR_CMD_EXPRESS_SCAN, struct.pack("<BI", mode, 0x00000000))
        self.__establishLoop(self.__capsuleUpdate)

        if self.dataDiscriptor.data_type == 0x82:
            self.capsuleType = PyRPlidarScanCapsule
        elif self.dataDiscriptor.data_type == 0x84:
            self.capsuleType = PyRPlidarScanUltraCapsule
        elif self.dataDiscriptor.data_type == 0x85:
            self.capsuleType = PyRPlidarScanDenseCapsule
        else:
            raise RPlidarProtocolError("RPlidar Error : scan data type is not supported")
        

            
    def isConnected(self)->bool:
        return self.lidarSerial and self.lidarSerial.isOpen()
        
    def getCombinedTrans(self)->translation:
        return self.combinedTranslation
    
    def forceScan(self)->None:
        """
            Initalizes a force scan. 
            Since force scans use the same return packets as normal scans it may apear that the lidarlib initalized a normal scan and not a force scan but all data will be handled properly
        """
        self.__sendCommand(RPLIDAR_CMD_FORCE_SCAN)
        self.__establishLoop(self.__standardUpdate)

    
    def mapIsDone(self)->None:
        """Handles all the cleanup that is needed when a scan map is done and a new one needs to be initalized"""
        self.lastMap=self.currentMap
        self.currentMap=lidarMap(self, mapID=self.lastMap.mapID+1, deadband=self.config.deadband, sensorThetaOffset=self.localTranslation.theta)
        if self.config.debugMode:
            print("map swap attempted")
            print(len(self.lastMap.getPoints()),self.lastMap.len, self.lastMap.mapID, self.lastMap.getRange(), self.lastMap.getHz(), self.lastMap.getPeriod())
            print(len(self.currentMap.getPoints()),self.currentMap.len ,self.currentMap.mapID)
        
        #print(self.currentMap.points==self.lastMap.points)

    def setCurrentLocalTranslation(self, translation:translation)->None:
        """
            Sets the lidars objects local translation. This translation should be used for the tranlation from the lidar to the center of the robot. 
            The translation will be added to all future points read by the lidar(untill changed) but will not be added to old retroactivly.
        """
        self.localTranslation=translation
        self.currentMap.setOffset(self.localTranslation.theta)
        self.combinedTranslation=self.localTranslation.combineTranslation(self.globalTranslation)

    def setCurrentGlobalTranslation(self, translation:translation)->None:
        """
            Sets the lidars objects local translation. This translation should be used for the translation between the robot and the 0,0 of the field 
            The translation will be added to all future points read by the lidar(untill changed) but will not be added to old retroactivly.
        """
        self.globalTranslation=translation
        self.combinedTranslation=self.globalTranslation.combineTranslation(self.localTranslation)


    def setDeadband(self, deadband:list[int])->None:
        """
            Sets a deadband of angles that will be dropped by the lidar. The droped angle is calculated after the local translation but before the global translation. 
            The inputed argument should be a list of ints in which the first argument is the start of the deadband and the second is the end. 
            If the second argument is larger than the first the deadband will be assumed to wrap past 360 degrees. 
        """
        self.config.deadband=deadband
        self.currentMap.setDeadband(
            
        )