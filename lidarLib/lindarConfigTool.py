import serial
from lidarLib.LidarConfigs import lidarConfigs
from serial.tools import list_ports
import pygame


def getInput(toPrint:str = None, shouldStrip:bool = True, shouldLower:bool = True):
    response = input(toPrint)
    if shouldStrip: response=response.strip()
    if shouldLower: response=response.lower()
    return response

class lidarConfigurationTool:

    def __init__(self):
        self.defaults = lidarConfigs.defaultConfigs
        self.configFile:lidarConfigs=None

        #opening
        self.opening()
        

        self.verboseCheck()

        #find lidar
        self.findLidar()


        #baudrate
        self.findBaudRate()

        #get trans


        #deadband

        #verbose checks

            #speed
            #id checks
            #auto start + connect
            #debug 
            #time
            #out


        #name

        #file write

        #test


        #quickstart tool??????

    def opening(self):
        
        response = getInput("Welcome the Wired lib lidar Config tool. If at any time you are confused type \"help\" and more information will be provided. Make sense? (y/n)")
        
        if response=='help':
            print("throughout the tool the character \'y\' will be used for yes and the character \'n\' will be used for no. If these responses are not working make sure your typing in lower case and then restart the tool.")

        elif response=="y":
            return
        
        elif response=="n":
            print("Try typing \"help\" for help")
            self.opening()
            return

        else:
            print("Sorry", response, "is not a valid response. Try y, n, or help. ")
            self.opening()
            return

    def verboseCheck(self):
        response = getInput("Would you like to run in verbose mode (only recommended for people with significant experience). (y/n)")
        
        if response=="help":
            print("Verbose mode provides the option to edit more volatile configs that may cause crashes if used wrong and should be defaulted most of the time.")
            self.verboseCheck()
            return

        elif response=='y':
            self.verbose=True
            

        elif response=='n':
            self.verbose=False

        else:
            print("Sorry", response, "is not a valid response. Try y, n, or help. ")
            self.verboseCheck()
            return

    def findLidar(self):
        trash = getInput("Please plug in EXACTLY 1 Slamtec lidar to be configured. Press enter to continue")
    


        portFound=None
        for bus in list_ports.comports():
            if bus.vid == self.defaults["vendorID"]:
                if self.configFile==None:
                    self.configFile = lidarConfigs(vendorID=bus.vid, productID=bus.pid, serialNumber=bus.serial_number)
                    self.portFound==bus.product
                else:
                    print("Detected multiple lidar like devices. Please make sure that there is only one lidar plugged in. If the issue continues please try on a different device.")
                    response = getInput("Would you like to enter the productID, vendorID, and serial number manually? (y/n)")
                    if response=='help':
                        print("It is possible for the config tool to mistake other devices for lidars. If this it the case you may choose to manually the values here.")
                    elif response == 'y':
                        self.enterSerialValuesManual()
                        break

                    self.configFile=None
                    self.findLidar()
                    return
                
        if self.verbose:
            print("Lidar found with vendorID:", self.configFile.vendorID, " productID:", self.configFile.productID, "serialPort:", self.configFile.serialNumber,)
            response = getInput("Does this look right?(y/n)")
            if response=='n':
                self.enterSerialValuesManual()

        else:
            print("Lidar Found!!!")




    def enterSerialValuesManual(self):
        shouldQuit = getInput("Would you like to continue setting the productID, vendorID, and serial number of the lidar manually (y/n)")
        if shouldQuit=="help":
            print(
                "This function allows you to manually set the vendorID, productID, and serial number of the lidar." 
                " This can be useful if the Config tool is having trouble finding the lidar."
            )

        elif( shouldQuit=='y'):
            return
        
        elif(shouldQuit=='n'):
            pass

        else:
            print("Sorry", shouldQuit, "is not a valid response. Try y, n, or help. ")
            self.enterSerialValuesManual()
            return

        vid = None
        while vid:
            vid = getInput("please enter the vendor ID in format 0xXXXX where X (but not x) is replaced with a hexadecimal number or press enter to use default")
            
            if len(vid)==0:
                vid=self.defaults["vendorID"]
            
            try:
                vid = hex(int(vid, 16))

            except:
                print("Vendor ID", vid, "Could not be converted into a hexadecimal integer. Likely it was formatted incorrectly")
                self.enterSerialValuesManual()
                vid=None
            
            if vid<0 or vid>0xffff:
                print("Vendor ID", vid, "Was not in valid range 0x0000 to 0xffff")
                vid=None

            isCorrect = getInput("VendorID will be set to", vid, ". Does this look correct?(y/n)")
            if isCorrect!='y':
                vid=None
            


        pid = None
        while pid:
            pid = getInput("please enter the product ID in format 0xXXXX where X (but not x) is replaced with a hexadecimal number.")

            try:
                pid = hex(int(pid, 16))

            except:
                print("Product ID", pid, "Could not be converted into a hexadecimal integer. Likely it was formatted incorrectly")
                self.enterSerialValuesManual()
                pid=None
            
            if pid<0 or pid>0xffff:
                print("Product ID", pid, "Was not in valid range 0x0000 to 0xffff")
                pid=None

            isCorrect = getInput("Product ID will be set to", pid, ". Does this look correct?(y/n)")
            if isCorrect!='y':
                pid=None



        serialNumber = None
        while serialNumber:
            serialNumber = getInput("please enter the serial number as a string (Make sure NOT to include a 0x at the beginning).")

            isCorrect = getInput("Product ID will be set to", serialNumber, ". Does this look correct?(y/n)")
            if isCorrect!='y':
                serialNumber=None


        response=None
        while not response:
            response = getInput("This will set the Vendor ID to", vid, ", the product id to", pid,", and the serial number to", serialNumber, ". Does this look correct?(y/n)")
            if response=='y':
                break
            elif response == 'n':
                isSure = None
                while not isSure:
                    isSure=getInput("Are you sure? saying yes will restart the manual process from the beginning. (y/n)")
                    if isSure=='y':
                        self.enterSerialValuesManual()
                        return
                    elif isSure=='n':
                        break
                    else:
                        print("Sorry", isSure, "is not a valid response. Try y or n. ")


            else:
                print("Sorry", response, "is not a valid response. Try y or n. ")
                response=None


        print("Values set!!!")
        self.configFile = lidarConfigs(vendorID=vid, productID=pid, serialNumber=serialNumber)


    def findBaudRate(self):
        baudrate = self.baudRateAutoTest()
        if baudrate=="Unknown":
            response = getInput(
                "The config tool could not automatically determine the baudrate of connected lidar. " 
                "Would you like to manually enter the baudrate (otherwise the system will try again)? (y/n)"
            )

            if response=='y':
                pass 

            elif response=="help":
                print(
                    "Baudrate tells the system how fast the lidar will send packages. " 
                    "If your lidar model has a 5pin to usb adapter it may have a switch on the side to change Baudrate with the numbers written on it. " 
                    "Otherwise check the specific models documentation to find the baudrate. ")
                self.findBaudRate()
                return
            elif response=='n':
                self.findBaudRate()
                return
            
            else:
                self.findBaudRate()
                print("Sorry", response, "is not a valid response. Try y or n. ")
                return
            
            baudrate=None
            while not baudrate:
                baudrate = getInput("Please enter the baudrate as a decimal integer.").strip()
                try:
                    baudrate = int(baudrate)
                except:
                    print("Could not convert", baudrate, "to a decimal integer. Please try again")
                    baudrate=0
                
                response= getInput("This will set the baudrate to", baudrate, ". Does this look correct?")
                if response=='y':
                    break
                elif response == 'n':
                    pass
                else:
                    print("Sorry", response, "is not a valid response. Try y or n. ")


        self.configFile.baudrate=baudrate


                

            

    def baudRateAutoTest(self, packet = b' '):
        

        for bus in list_ports.comports():
            if bus.serial_number == self.configFile.serialNumber and bus.vid == self.configFile.vendorID and bus.pid == self.configFile.productID:
                port = bus.device

        ser = serial.Serial(port)
        ser.timeout = 0.5
        for baudrate in [115200, 256000]:
            ser.baudrate = baudrate
            ser.write(packet)
            resp = ser.readall()
            if resp == packet:
                return baudrate
        return 'Unknown'
    

def getTrans():
        
    pygame.init()


    displayWidth = 400
    displayHeight = 400

    gameDisplay = pygame.display.set_mode((displayWidth,displayHeight))
    pygame.display.set_caption('Translation demo')

    black = (0,0,0)
    white = (255,255,255)

    clock = pygame.time.Clock()
    carImg = pygame.image.load('lidarLib/robot.png')
    lidarImg = pygame.image.load('lidarLib/lidar.png')

    x, y, r= 0, 0, 0
    

    def draw():

        gameDisplay.fill(white)
        gameDisplay.blit(carImg, ((displayWidth-332)/2, (displayHeight-332)/2))
        gameDisplay.blit(lidarImg, (displayWidth/2 + x/400, displayHeight/2 + y/400, r))
        pygame.display.update()

    draw()
        
  

    while True:
        pass
    # x=None
    # while not x:
    #     x = input("Please input the X value of the translation to the lidar")


    pygame.quit()




if __name__ == '__main__':
    
    lidarConfigurationTool()

