import json


from lidarLib import lidarProtocol
from lidarLib.translation import translation




class lidarConfigs:


    defaultConfigs = {
                
        "port" : None,
        "localTrans": translation.default(),
        "baudrate" : 256000,
        "deadband" : None,
        "timeout" : 3,
        "mode"  : "normal",
        "debugMode" : False,
        "isStop" : False,
        "autoStart" : False,
        "autoConnect" : True,
        "defaultSpeed" : lidarProtocol.RPLIDAR_DEFAULT_MOTOR_PWM,
        "reportData" : True,
        "reportSampleRate" : True,
        "reportCombinedOffset" : True,
        "reportScanModes" : True
    }




    def __init__(
                    self, 
                    port:string,
                    localTrans = defaultConfigs['localTrans'], 
                    baudrate = defaultConfigs["baudrate"], 
                    timeout=defaultConfigs["timeout"], 
                    mode=defaultConfigs["mode"], 
                    deadband=defaultConfigs["deadband"], 
                    debugMode=defaultConfigs["debugMode"],
                    isStop=defaultConfigs["isStop"], 
                    autoStart=defaultConfigs["autoStart"], 
                    autoConnect=defaultConfigs["autoStart"], 
                    defaultSpeed=defaultConfigs["defaultSpeed"],
                    reportData=defaultConfigs["reportData"], 
                    reportSampleRate=defaultConfigs["reportSampleRate"], 
                    reportScanModes=defaultConfigs["reportScanModes"], 
                    reportCombinedOffset=defaultConfigs["reportScanModes"]
            ):

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
                        data.get("localTrans").get("x", lidarConfigs.defaultConfigs["localTrans"].x),
                        data.get("localTrans").get("y", lidarConfigs.defaultConfigs["localTrans"].y),
                        data.get("localTrans").get("rotation", lidarConfigs.defaultConfigs["localTrans"].rotation)
                    ),
                    baudrate = data.get("baudrate", lidarConfigs.defaultConfigs["baudrate"]),
                    deadband = data.get("deadband", lidarConfigs.defaultConfigs["deadband"]),
                    timeout = data.get("timeout", lidarConfigs.defaultConfigs["timeout"]),
                    mode  = data.get("mode", lidarConfigs.defaultConfigs["mode"]),
                    debugMode = data.get("debugMode", lidarConfigs.defaultConfigs["debugMode"]),
                    isStop = data.get("isStop", lidarConfigs.defaultConfigs["isStop"]),
                    autoStart = data.get("autoStart", lidarConfigs.defaultConfigs["autoStart"]),
                    autoConnect = data.get("autoConnect", lidarConfigs.defaultConfigs["autoConnect"]),
                    defaultSpeed = data.get("defaultSpeed", lidarConfigs.defaultConfigs["defaultSpeed"]),
                    reportData = data.get("reportData", lidarConfigs.defaultConfigs["reportData"]),
                    reportSampleRate = data.get("reportSampleRate", lidarConfigs.defaultConfigs["reportSampleRate"]),
                    reportScanModes = data.get("reportScanModes", lidarConfigs.defaultConfigs["reportScanModes"]),
                    reportCombinedOffset = data.get("reportCombinedOffset", lidarConfigs.defaultConfigs["reportCombinedOffset"])
                )
            


        except FileNotFoundError:
            print(f"Error: File not found at path: [path]")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file: [path]")
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

            keysToRemove = []
            for key in data.keys():
                if data[key] == lidarConfigs.defaultConfigs[key]:
                    keysToRemove.append(key)

            for key in keysToRemove:
                data.pop(key)
            

            with open(path, 'w') as file:
                json.dump(data, file, indent=4)                


        except FileNotFoundError:
            print(f"Error: File not found at path: [path]")
            return None




