import string
import serial


class RPlidarSerial:
    """Class to handle the serial bus used by a lidar"""
    def __init__(self):
        self.serial = None

    def open(self, port:string, baudrate:int, timeout:int)->None:
        """
            Opens a serial port on the specified port and with the specified baud rate. 
            Will print a warning but not throw an error if the port can not be opened. This error checking should be managed somewhere else
        """
        if self.serial is not None:
            self.close()
        try:
            self.serial = serial.Serial(port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=timeout, dsrdtr=True)
        except serial.SerialException as err:
            print("Failed to connect to the rplidar")
    
    def close(self)->None:
        """Closes and dereferences the internal serial port"""
        if self.serial is None:
            return
        self.serial.close()
        self.serial=None
    
   
    
    def sendData(self, data:bytes)->None:
        """sends the specified data through the serial port"""
        self.serial.write(data)
    
    def receiveData(self, size:int)->bytes:
        """Recives and returns the specified number of bytes from the serial port. if not enough bytes are available all that are will be returned"""
        return self.serial.read(size)

    def setDtr(self, value:int)->None:
        """sets the dtr of the internal serial port. Whenever the port is closed this value will be lost and need to be reset"""
        self.serial.dtr = value

    def isOpen(self)->bool:
        """returns wether or not the internal port is open"""
        return self.serial!=None 
    

    def bufferSize(self)->int:
        """returns the number of Bytes currently in the serial buffer"""
        if self.isOpen():
            return self.serial.in_waiting


    def flush(self)->None:
        """flushes the serial buffer"""
        self.serial.reset_input_buffer()
        