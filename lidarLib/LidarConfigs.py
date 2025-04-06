import string
import json


from lidarLib.translation import translation


class lidarConfigs:
    def __init__(self, port:string, localTrans = translation.default(), baudrate = 256000, timeout=3, deadband=None, debugMode=False,
                isStop=False, autoStart=False, autoConnect=True, defaultSpeed=0, reportData=True, reportSampleRate=True, reportScanModes=True, reportCombinedOffset=True, mode="normal"):
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
    @DeprecationWarning
    def configsFromJson(cls:"lidarConfigs", path:string):
        try:
            with open(path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found at path: {path}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file: {path}")
            return None


        return cls(
            data["port"], 
            translation.fromCart(data["localTrans"]['x'], data["localTrans"]['y'], data["localTrans"]['rotation']),
            data["baudrate"],
            data["deadband"],
            data["debugMode"],
            data["isStop"],
            data["autoStart"],
            data["defaultSpeed"],
            data["reportData"],
            data["reportSampleRate"],
            data["reportScanModes"],
            data["reportCombinedOffset"]
            )