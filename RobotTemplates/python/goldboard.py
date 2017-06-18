
class motor:
	def __init__(self):
	



class goldboard:
	def __init__(self):
		self.motor = motor[4]
		self.serial = serial()
		self.compass = compass()
		self.sonar = sonar[4]
		self.usring = usring

	#Puts off all motors.
	def setMotorsOff(self):
		for m in self.motor:
			m.speed = 0
	
	#Sets a motor offset
	def setMotorsOffset(self, value):
		for m in self.motor:
			m.offset = value

	
	#Puts the power output i on if state is true, else off
	def setPower(self, i, state):
		if i == 0:
			self.dribbler = state
		if i == 1:
			self.kicker = state

	# Checks the state of button i. If it is pressed, true is returned,  else false.
	#	def getButton(self, i):
	
	# Waits until button i is pressed and released again.
	# void waitForButton(uint8_t i):

	# returns the value of the analog port i. 0 <= value <= 255
	def getAnalog(self, i):
		return 0

	# returns true if the pwm port is logical high, else false.
	def getPWM(uint8_t i):
		return 0
	
	# returns true if the digital port is logical high, else false.
	def getDigital(uint8_t i):
		return 0

	# returns the registered pulse length of the digital port i. 0 <= value <= 255
	def getDigitalPulsedLight(uint8_t i):
		return 0

	# returns the registered pulse length of the pwm port i. 0 <= value <= 255
	def getPWMPulsedLight(uint8_t i):
		return 0