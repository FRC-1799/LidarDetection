import string
import json


from lidarLib.translation import translation




class lidarConfigs:


    defaultLocalTrans = translation.default()
    defaultBaudrate = 256000
    defaultTimeout=3, deadband=None, debugMode=False,
    defaultIsStop=False
    defaultAutoStart=False
    defaultAutoConnect=True
    defaultDefaultSpeed=0
    defaultDeadband=None
    defaultDebugMode = False
    defaultReportData=True
    defaultReportSampleRate=True
    defaultReportScanModes=True
    defaultReportCombinedOffset=True
    defaultMode="normal"


    def __init__(self, port:string, localTrans = defaultLocalTrans, baudrate = defaultBaudrate, timeout=defaultTimeout, mode=defaultMode, deadband=defaultDeadband, debugMode=defaultDebugMode,
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

        if debugMode:
            self.printConfigs()
            
    def printConfigs(self):
        print("new lidarConfig created with args", 
            "\nport:", self.port,
            "\nlocalTrans:", self.localTrans,
            "\nbaudrate:", self.baudrate,
            "\ndeadband:", self.deadband,
            "\ndebugMode:", self.debugMode,
            "\nisStop:", self.isStop,
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
    def configsFromJson(cls:"lidarConfigs", path:string):
        try:
            with open(path, 'r') as file:
                data:dict = json.load(file)

                return cls(
                    port = data.get("port"), 
                    translation = translation.fromCart(file.get("localTrans").get("x", lidarConfigs.defaultLocalTrans.getX()), file.get("localTrans").get("y", lidarConfigs.defaultLocalTrans.getY()), file.get("localTrans").get("rotation", lidarConfigs.defaultLocalTrans.getRotation())),
                    baudrate = data.get("baudrate", lidarConfigs.defaultBaudrate),
                    timeout = data.get("deadband", lidarConfigs.defaultTimeout),
                    mode  = data.get("mode", lidarConfigs.defaultMode),
                    debugMode = data("debugMode", lidarConfigs.defaultDebugMode),
                    isStop = data.get("isStop", lidarConfigs.defaultIsStop),
                    autoStart = data.get("autoStart", lidarConfigs.defaultAutoStart),
                    autoConnect = data.get("autoConnect", lidarConfigs.defaultAutoConnect),
                    defaultSpeed = data.get("defaultSpeed", lidarConfigs.defaultDefaultSpeed),
                    reportData = data.get("reportData", lidarConfigs.defaultReportData),
                    reportSampleRate = data.get("reportSampleRate", lidarConfigs.defaultReportSampleRate),
                    reportScanModes = data.get("reportScanModes", lidarConfigs.defaultReportScanModes),
                    reportCombinedOffset = data("reportCombinedOffset", lidarConfigs.defaultReportCombinedOffset)
                )
            


        except FileNotFoundError:
            print(f"Error: File not found at path: {path}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file: {path}")
            return None



