import serial

class Teensy:
	def __init__(self, port, baudrate):
		self.port = port
		self.baudrate = baudrate

	def connect(self):
		self.port = serial.Serial(self.port, self.baudrate)

	def motor_absolute(self, position):
		s = "m a " + str(position) + "\n"
		print("Sending command: " + s)
		self.write(s.encode())

	def write(self, string):
		self.port.write(string)


