
from time import sleep
from lidarLib.pyrplidarSerial import PyRPlidarSerial
from lidarLib.lidarProtocol import *
import lidarLib.lidarProtocol
from lidarLib.lidarMap import lidarMap
import threading



class Lidar:

    def __init__(self):
        self.lidarSerial = None
        self.measurements = None
        self.currentMap=lidarMap(self)
        self.lastMap=None
        #self.eventLoop()
        
        self.capsuleType=None
        self.loop = None
        self.dataDiscriptor=None
        self.isDone=False

    
    def __del__(self):
        
        self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exceptionType, exceptionValue, exceptionTraceback):
        self.disconnect()

    def connect(self, port="/dev/ttyUSB0", baudrate=115200, timeout=3):
        self.lidarSerial = PyRPlidarSerial()
        self.lidarSerial.open(port, baudrate, timeout)
        
        if self.lidarSerial.isOpen():
            print("PyRPlidar Info : device is connected")
        else:
            self.readToCapsule=None
            raise ConnectionError("could not find lidar unit")
        



    def establishLoop(self, updateFunc):
        self.update=updateFunc
        self.dataDiscriptor = self.receiveDiscriptor()
        self.loop = threading.Thread(target=self.updateLoop, daemon=False)
        self.loop.start()

    def disconnect(self, leaveRunning=False):
        
        if self.lidarSerial is not None:
            self.isDone=True
            if not leaveRunning:
                self.stop()
                self.set_motor_pwm(0)
            self.lidarSerial.close()
            
            self.lidarSerial = None
            print("PyRPlidar Info : device is disconnected")

    def updateLoop(self):
        while not self.isDone:
            self.update()
            sleep(0.001)
            
        

    def update(self):
        
        raise PyRPlidarProtocolError("Update was called without a valid connection established, this may because a user tried to call it")


    def standardUpdate(self):
        
        while not self.isDone:
            #print(self.lidarSerial.bufferSize())
            if self.dataDiscriptor and (self.lidarSerial.bufferSize()>=self.dataDiscriptor.data_length):
                #print("update working")
                newData=lidarMeasurement(self.receiveData(self.dataDiscriptor))
                self.currentMap.addVal(newData)
            else:
                #print("break hit")
                break
        
        #print("thingy")

    def capsuleUpdate(self):
        data = self.receiveData(self.dataDiscriptor)
        capsule_prev = self.capsuleType(data)
        capsule_current = None
        
        while not self.isDone:
            if self.dataDiscriptor and (self.lidarSerial.bufferSize()>=self.dataDiscriptor.data_length):
                data = self.receiveData(self.dataDiscriptor)
                capsule_current = self.capsuleType(data)
                
                nodes = self.capsuleType._parse_capsule(capsule_prev, capsule_current)
                for index, node in enumerate(nodes):
                        self.currentMap.addVal(lidarMeasurement(raw_bytes=None, measurement_hq=node))

                capsule_prev = capsule_current
            else:
                break



        

    def sendCommand(self, cmd, payload=None):
        if self.lidarSerial == None:
            raise PyRPlidarConnectionError("PyRPlidar Error : device is not connected")

        self.lidarSerial.send_data(PyRPlidarCommand(cmd, payload).raw_bytes)

    def receiveDiscriptor(self):
        if self.lidarSerial == None:
            raise PyRPlidarConnectionError("PyRPlidar Error : device is not connected")
        
        discriptor = PyRPlidarResponse(self.lidarSerial.receive_data(RPLIDAR_DESCRIPTOR_LEN))
        
        if discriptor.sync_byte1 != RPLIDAR_SYNC_BYTE1[0] or discriptor.sync_byte2 != RPLIDAR_SYNC_BYTE2[0]:
            raise PyRPlidarProtocolError("PyRPlidar Error : sync bytes are mismatched", hex(discriptor.sync_byte1), hex(discriptor.sync_byte2))
        return discriptor

    def receiveData(self, discriptor):
        
        if self.lidarSerial == None:
            raise PyRPlidarConnectionError("PyRPlidar Error : device is not connected")
        
        data = self.lidarSerial.receive_data(discriptor.data_length)
        if len(data) != discriptor.data_length:
            raise PyRPlidarProtocolError()
        return data



    def stop(self):
        self.sendCommand(RPLIDAR_CMD_STOP)

    def reset(self):
        self.sendCommand(RPLIDAR_CMD_RESET)

    def set_motor_pwm(self, pwm):
        self.lidarSerial.set_dtr(False)
        self.sendCommand(RPLIDAR_CMD_SET_MOTOR_PWM, struct.pack("<H", pwm))
    
    

    def getInfo(self):
        self.sendCommand(RPLIDAR_CMD_GET_INFO)
        discriptor = self.receiveDiscriptor()
        data = self.receiveData(discriptor)
        return PyRPlidarDeviceInfo(data)

    def getHealth(self):
        self.sendCommand(RPLIDAR_CMD_GET_HEALTH)
        discriptor = self.receiveDiscriptor()
        data = self.receiveData(discriptor)
        return PyRPlidarHealth(data)

    def getSamplerate(self):
        self.sendCommand(RPLIDAR_CMD_GET_SAMPLERATE)
        discriptor = self.receiveDiscriptor()
        data = self.receiveData(discriptor)
        return PyRPlidarSamplerate(data)

    def getLidarConf(self, payload):
        self.sendCommand(RPLIDAR_CMD_GET_LIDAR_CONF, payload)
        discriptor = self.receiveDiscriptor()
        data = self.receiveData(discriptor)
        return data

    def get_scan_mode_count(self):
        data = self.getLidarConf(struct.pack("<I", RPLIDAR_CONF_SCAN_MODE_COUNT))
        count = struct.unpack("<H", data[4:6])[0]
        return count

    def getScanModeTypical(self):
        data = self.getLidarConf(struct.newPointpack("<I", RPLIDAR_CONF_SCAN_MODE_TYPICAL))
        typical_mode = struct.unpack("<H", data[4:6])[0]
        return typical_mode

    def getScanModes(self):
        
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


    def startScan(self):
        self.sendCommand(RPLIDAR_CMD_SCAN)
        self.establishLoop(self.standardUpdate)

    
    def startScanExpress(self, mode):
        
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
        

            

        

    
    def forceScan(self):
        self.sendCommand(RPLIDAR_CMD_FORCE_SCAN)
        self.establishLoop(self.standardUpdate)

    
    def mapIsDone(self):
        print("map swap attempted")
        self.lastMap=self.currentMap
        self.currentMap=lidarMap(self, mapID=self.lastMap.mapID+1)
        print(len(self.currentMap.getPoints()), self.currentMap.mapID)
        print(len(self.lastMap.getPoints()), self.lastMap.mapID)

    def getCurrentMap(self):
        return self.currentMap

