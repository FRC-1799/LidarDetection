
from lidarLib.pyrplidarSerial import PyRPlidarSerial
from lidarLib.lidarProtocol import *
import lidarLib.lidarProtocol
from lidarLib.lidarMap import lidarMap
from threading import Timer
import time



class Lidar:

    def __init__(self, hz=400):
        self.lidarSerial = None
        self.measurements = None
        self.currentMap=lidarMap(self)
        self.lastMap=None
        
        self.hz=hz
        self.timer = None
        self.dataDiscriptor=None

    
    def __del__(self):
        
        self.disconnect()

    

    def connect(self, port="/dev/ttyUSB0", baudrate=115200, timeout=3):
        self.lidarSerial = PyRPlidarSerial()
        self.lidarSerial.open(port, baudrate, timeout)
        self.rebootTimer()
        if self.lidarSerial.isOpen():
            print("PyRPlidar Info : device is connected")
        else:
            raise ConnectionError("could not find lidar unit")
        # self.reset()
        # self.lidarSerial.flush()
        
    def rebootTimer(self):
        self.timer = Timer(1/self.hz, self.update)
        self.timer.start()

    def disconnect(self, leaveRunning=False):
        
        if self.lidarSerial is not None:
            if not leaveRunning:
                self.stop()
                self.set_motor_pwm(0)
            self.lidarSerial.close()
            self.timer.cancel()
            self.lidarSerial = None
            print("PyRPlidar Info : device is disconnected")

    def update(self):
        
        while True:
            if self.dataDiscriptor and (self.lidarSerial.bufferSize()>=self.dataDiscriptor.data_length):
            
                newData=lidarMeasurement(self.receiveData(self.dataDiscriptor))
                self.currentMap.addVal(newData)
            else:
                break
        self.rebootTimer()
        #print("thingy")

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
        #self.reset()
        #time.sleep(0.01)
        #self.lidarSerial.flush()
        self.sendCommand(RPLIDAR_CMD_SCAN)
        
        self.dataDiscriptor = self.receiveDiscriptor()

    @DeprecationWarning
    def startScanExpress(self, mode):
        
        self.sendCommand(RPLIDAR_CMD_EXPRESS_SCAN, struct.pack("<BI", mode, 0x00000000))
        discriptor = self.receiveDiscriptor()

        if discriptor.data_type == 0x82:
            capsule_type = PyRPlidarScanCapsule
        elif discriptor.data_type == 0x84:
            capsule_type = PyRPlidarScanUltraCapsule
        elif discriptor.data_type == 0x85:
            capsule_type = PyRPlidarScanDenseCapsule
        else:
            raise PyRPlidarProtocolError("RPlidar Error : scan data type is not supported")
        
        def scanGenerator():
            
            data = self.receiveData(discriptor)
            capsule_prev = capsule_type(data)
            capsule_current = None
            
            while True:
                data = self.receiveData(discriptor)
                capsule_current = capsule_type(data)
                
                nodes = capsule_type._parse_capsule(capsule_prev, capsule_current)
                for index, node in enumerate(nodes):
                     yield lidarMeasurement(raw_bytes=None, measurement_hq=node)
    
                capsule_prev = capsule_current

        return scanGenerator

    
    def forceScan(self):
        self.sendCommand(RPLIDAR_CMD_FORCE_SCAN)
        self.dataDiscriptor = self.receiveDiscriptor()

    
    def mapIsDone(self):
        print(len(self.currentMap.getPoints()))
        self.currentMap.printMap()
        if len(self.currentMap.getPoints())<10:
            raise ValueError()
        self.lastMap=self.currentMap
        self.currentMap=lidarMap(self)
        print("New map \n\n\n\n")

    def getCurrentMap(self):
        return self.currentMap

