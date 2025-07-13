import json


from lidarLib import lidarProtocol
from lidarLib.translation import translation




class lidarConfigs:


    defaultLocalTrans = translation.default()
    defaultBaudrate = 256000
    defaultTimeout=3 
    deadband=None
    debugMode=False
    defaultIsStop=False
    defaultAutoStart=False
    defaultAutoConnect=True
    defaultDefaultSpeed=lidarProtocol.RPLIDAR_DEFAULT_MOTOR_PWM
    defaultDeadband=None
    defaultDebugMode = False
    defaultReportData=True
    defaultReportSampleRate=True
    defaultReportScanModes=True
    defaultReportCombinedOffset=True
    defaultMode="normal"


    def __init__(self, port:str, localTrans = defaultLocalTrans, baudrate = defaultBaudrate, timeout=defaultTimeout, mode=defaultMode, deadband=defaultDeadband, debugMode=defaultDebugMode,
                isStop=defaultIsStop, autoStart=defaultAutoStart, autoConnect=defaultAutoConnect, defaultSpeed=defaultDefaultSpeed,
                reportData=defaultReportData, reportSampleRate=defaultReportSampleRate, reportScanModes=defaultReportScanModes, reportCombinedOffset=defaultReportCombinedOffset):
        self.port=port
        self.localTrans = localTrans
        self.baudrate = baudrate
        self.timeout=timeout
        self.deadband=deadband
        self.debugMode=debugMode
        self.isStop=isStop
        self.autoStart=autoStart
        self.defaultSpeed = defaultSpeed
        self.reportData = reportData
        self.reportSampleRate=reportSampleRate
        self.reportScanModes=reportScanModes
        self.reportCombinedOffset = reportCombinedOffset
        self.mode=mode
        self.autoConnect=autoConnect
        self.deadband = deadband

        if debugMode:
            self.printConfigs()
            
    def printConfigs(self):
        print("lidarConfig args", 
            "\nport:", self.port,
            "\nlocalTrans:", self.localTrans,
            "\nbaudrate:", self.baudrate,
            "\ndeadband:", self.deadband,
            "\ndebugMode:", self.debugMode,
            "\nisStop:", self.isStop,
            "\ntimeout: ", self.timeout,
            "\nautoStart:", self.autoStart,
            "\nautoConnect:", self.autoConnect,
            "\ndefualtSpeed:", self.defaultSpeed,
            "\nreportData:", self.reportData,
            "\nreportSampleRate:", self.reportSampleRate,
            "\nreportScanModes:", self.reportScanModes,
            "\nreportCombinedOffset:", self.reportCombinedOffset  ,
            "\nmode:", self.mode           
        )

    @classmethod
    def configsFromJson(cls:"lidarConfigs", path:string)->"lidarConfigs":
        try:
            with open(path, 'r') as file:
                data:dict = json.load(file)

                return cls(
                    port = data.get("port"), 
                    localTrans = translation.fromCart(
                        data.get("localTrans").get("x", lidarConfigs.defaultLocalTrans.x),
                        data.get("localTrans").get("y", lidarConfigs.defaultLocalTrans.y),
                        data.get("localTrans").get("rotation", lidarConfigs.defaultLocalTrans.rotation)
                    ),
                    baudrate = data.get("baudrate", lidarConfigs.defaultBaudrate),
                    deadband = data.get("deadband", lidarConfigs.defaultTimeout),
                    timeout = data.get("timeout", lidarConfigs.defaultDeadband),
                    mode  = data.get("mode", lidarConfigs.defaultMode),
                    debugMode = data.get("debugMode", lidarConfigs.defaultDebugMode),
                    isStop = data.get("isStop", lidarConfigs.defaultIsStop),
                    autoStart = data.get("autoStart", lidarConfigs.defaultAutoStart),
                    autoConnect = data.get("autoConnect", lidarConfigs.defaultAutoConnect),
                    defaultSpeed = data.get("defaultSpeed", lidarConfigs.defaultDefaultSpeed),
                    reportData = data.get("reportData", lidarConfigs.defaultReportData),
                    reportSampleRate = data.get("reportSampleRate", lidarConfigs.defaultReportSampleRate),
                    reportScanModes = data.get("reportScanModes", lidarConfigs.defaultReportScanModes),
                    reportCombinedOffset = data.get("reportCombinedOffset", lidarConfigs.defaultReportCombinedOffset)
                )
            


        except FileNotFoundError:
            print(f"Error: File not found at path: {path}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file: {path}")
            return None

    def writeToJson(self, path:string):
        try:
            data = {
                
                "port" : self.port,
                "localTrans": {
                    "x":self.localTrans.x,
                    "y":self.localTrans.y,
                    "rotation":self.localTrans.rotation
                },
                "baudrate" : self.baudrate,
                "deadband" : self.deadband,
                "timeout" : self.timeout,
                "mode"  : self.mode,
                "debugMode" : self.debugMode,
                "isStop" : self.isStop,
                "autoStart" : self.autoStart,
                "autoConnect" : self.autoConnect,
                "defaultSpeed" : self.defaultSpeed,
                "reportData" : self.reportData,
                "reportSampleRate" : self.reportSampleRate,
                "reportScanModes" : self.reportScanModes,
                "reportCombinedOffset" : self.reportCombinedOffset
            }

            with open(path, 'w') as file:
                json.dump(data, file)                


        except FileNotFoundError:
            print(f"Error: File not found at path: {path}")
            return None




