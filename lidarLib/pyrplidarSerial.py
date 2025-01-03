import string
import serial


class PyRPlidarSerial:
    
    def __init__(self):
        self.serial = None

    def open(self, port:string, baudrate:int, timeout:int)->None:
        if self.serial is not None:
            self.close()
        try:
            self.serial = serial.Serial(port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=timeout, dsrdtr=True)
        except serial.SerialException as err:
            print("Failed to connect to the rplidar")
    
    def close(self)->None:
        if self.serial is None:
            return
        self.serial.close()
        self.serial=None
    
   
    
    def send_data(self, data:bytes)->None:
        self.serial.write(data)
    
    def receive_data(self, size:int)->bytes:
        return self.serial.read(size)

    def set_dtr(self, value:int)->None:
        self.serial.dtr = value

    def isOpen(self)->bool:
        return self.serial!=None 
    

    def bufferSize(self)->int:
        if self.isOpen():
            return self.serial.in_waiting


    def flush(self)->None:
        self.serial.reset_input_buffer()
        