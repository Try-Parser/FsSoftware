from GTSensor import GTSensor
from GTEnum import GT521F5
from time import sleep 
import base64
import json

class App:
	def __init__(self):
		self.sensor = GTSensor('/dev/ttyAMA0', timeout=2, baudrate=9600)
		
		self.enrollment = False
		self.enrollmentCounter = 0

		self.userId = ""
		self.enrollmentCandidate = 0
		self.cancelEnroll = False

		print ("Setting baudrate from 9600 to 57600")
		baudrateResult = self.sensor.setBaudrate(57600)
		print ("baudrate :" + str(baudrateResult));
		print ("Setting is done testing for LED lights")
		self.sensor.LED(True)
		sleep(1)
		self.sensor.LED(False)

	def setEnrollment(self, args):
		self.enrollment = True
		self.userId = args["userId"]

	def getId(self):
		id = 0

		while True and id <= 2999 :
			resp = self.sensor.checkEnrolled(id)
			print(resp);

			if GT521F5.ERRORS.value[resp["Parameter"]] is not 'NACK_IS_NOT_USED':
				break			

	def enroll(self):
		confirmed = self.sensor.startEnrollment()
		if confirmed["ACK"]:
			self.sensor.LED(True)

	def switch(self, enrollmentIndex):
		switcher = {
			0: self.sensor.startEnrollment(self.enrollmentCandidate),
			1: self.sensor.enrollmentFirst(),
			2: self.sensor.enrollmentSecond(),
			3: self.sensor.enrollmentThird()
		}

		response = switcher.get(index, "Invalid index")

		print(response)

	def pressedFinger(self, channel):
		if self.enrollment and enrollment >= 3: 
			return self.enroll()
		else:
			return {'nothing: aw'}

		self.sensor.LED(True)
		sleep(1)
		self.sensor.LED(False)
