import serial


class PyRPlidarSerial:
    
    def __init__(self):
        self.serial = None

    def open(self, port, baudrate, timeout):
        if self.serial is not None:
            self.close()
        try:
            self.serial = serial.Serial(port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=timeout, dsrdtr=True)
        except serial.SerialException as err:
            print("Failed to connect to the rplidar")
    
    def close(self):
        if self.serial is None:
            return
        self.serial.close()
        self.serial=None
    
    def wait_data(self):
        pass
    
    def send_data(self, data):
        self.serial.write(data)
    
    def receive_data(self, size):
        return self.serial.read(size)

    def set_dtr(self, value):
        self.serial.dtr = value

    def isOpen(self):
        return self.serial!=None 
    

    def bufferSize(self):
        if self.isOpen():
            return self.serial.in_waiting


    def flush(self):
        self.serial.reset_input_buffer()