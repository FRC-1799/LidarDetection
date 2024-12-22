import serial


class PyRPlidarSerial:
    
    def __init__(self):
        self.serial = None

    def open(self, port, baudrate, timeout):
        if self.serial is not None:
            self.disconnect()
        try:
            self.serial = serial.Serial(port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=timeout, dsrdtr=True)
        except serial.SerialException as err:
            print("Failed to connect to the rplidar")
    
    def close(self):
        if self.serial is None:
            return
        self.serial.close()
    
    def wait_data(self):
        pass
    
    def send_data(self, data):
        self.serial.write(data)
    
    def receive_data(self, size):
        return self.serial.read(size)

    def set_dtr(self, value):
        self.serial.dtr = value

    def isOpen(self):
        return self.serial!=None and self.serial.isOpen()
