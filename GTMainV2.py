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
		candidate_id = 1

		while True and candidate_id <= 2999 :
			resp = self.sensor.checkEnrolled(candidate_id)
			print(resp);

			if resp["Parameter"] is 'NACK_IS_NOT_USED':
				self.enrollmentCandidate = candidate_id
				break;

	def __capture_the_lights__(self):
	        if self.sensor.senseFinger()[0]['Parameter'] == 0:
	                print ("Capturing Fingerprint")
	                sleep(0.1)
	                if self.sensor.captureFinger(True)['ACK']:
	                        print ("Captured")
	                        self.sensor.LED(False)
	                        return True

	def switch(self, enrollmentIndex):
		switcher = {
			0: self.sensor.startEnrollment(self.enrollmentCandidate),
			1: self.sensor.enrollmentFirst(),
			2: self.sensor.enrollmentSecond(),
			3: self.sensor.enrollmentThird()
		}

		response = switcher.get(enrollmentIndex, "Invalid Index")

		return response

	def pressedFinger(self, channel):
		print("Fingerpressed.")
		print(self.enrollmentCounter)
		if self.enrollment and self.enrollmentCounter <= 3:
			if self.enrollmentCounter is 0:
				self.getId()
			response = self.switch(self.enrollmentCounter)
			print(response)
			if response["ACK"]:
				self.sensor.LED(True)
				while not self.__capture_the_lights__():
					if self.cancelEnroll:
						break
				self.enrollmentCounter += 1
				self.sensor.LED(False)
		else:
			self.enrollmentCounter = 0
			self.enrollment = False
