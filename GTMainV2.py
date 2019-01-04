from GTSensor import GTSensor
from GTEnum import GT521F5
from time import sleep 
import base64
import json
import datetime


class App:
	def __init__(self):
		self.sensor = GTSensor('/dev/ttyAMA0', timeout=2, baudrate=9600)
		
		self.socket = ""

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

	def setSocket(self, ws):
		self.socket = ws

	def setEnrollment(self, args):
		self.enrollment = True
		print(self.enrollment)
		self.userId = args["userId"]

	def cancelEnrollment(self):
		self.cancelEnroll = True
		self.enrollment = False
		self.enrollmentCounter = 0
		self.userId = ""
		self.enrollmentCandidate = 0

	def clearDb(self):
		response = self.sensor.rmAll()
		print(response)

	def getId(self):
		candidate_id = 0

		while True and candidate_id <= 2999 :
			resp = self.sensor.checkEnrolled(candidate_id)
			print(resp);

			if resp["Parameter"] is 'NACK_IS_NOT_USED':
				self.enrollmentCandidate = candidate_id
				break;
			else:
				candidate_id += 1

	def __capture_the_lights__(self):
	        if self.sensor.senseFinger()[0]['Parameter'] == 0:
	                print ("Capturing Fingerprint")
	                sleep(0.1)
	                if self.sensor.captureFinger(True)['ACK']:
	                        print ("Captured")
	                        self.sensor.LED(False)
	                        return True

	def switch(self, enrollmentIndex):
		if enrollmentIndex is 0:
			print("candidate_id : " + str(self.enrollmentCandidate))
			return self.sensor.startEnrollment(self.enrollmentCandidate)
		elif enrollmentIndex is 1:
			return self.sensor.enrollmentFirst()
		elif enrollmentIndex is 2:
			return self.sensor.enrollmentSecond()
		elif enrollmentIndex is 3:
			return self.sensor.enrollmentThird()
		elif enrollmentIndex is 4:
			return self.sensor.generateTemplateById(self.enrollmentCandidate)

	def numberFormat(self, number): 
		if number < 10:
			return "0"+str(number)
		else:
			return str(number)

	def saveTemplate(self, template, index):
		response = self.sensor.setTemplate(template, index)
		print(response)
		if response[0]["ACK"]:
			return "successful"
		else:
			return response["Parameter"]

	def pressedFinger(self, channel):
		print("Fingerpressed.")
		print(self.enrollment)

		if self.enrollment and self.enrollmentCounter <= 3:

			if self.enrollmentCounter is 0:
				self.getId()
				resp = self.switch(self.enrollmentCounter)
				if resp["ACK"]:
					self.enrollmentCounter += 1
				print(self.enrollmentCandidate)

			response = self.switch(self.enrollmentCounter)
			print(response)

			if response["ACK"]:
				self.sensor.LED(True)

				while not self.__capture_the_lights__():
					if self.cancelEnroll:
						break

				self.enrollmentCounter += 1
				print(self.enrollmentCounter)

				if self.enrollmentCounter is 4:
					templateResponse = self.switch(self.enrollmentCounter)
					if templateResponse[0]['ACK']:
						preparedPayLoad = '{ "command": "W_REGED", "template": "'+ base64.b64encode(templateResponse[1]['Data']).decode() +'", "userId":"'+str(self.userId)+'", "scannerId":'+str(self.enrollmentCandidate)+'}'
						self.socket.send(preparedPayLoad)
						print("payload send")
			elif not response["ACK"] and response["Parameter"] is 0:

				print("Fingerprint is used")
				self.enrollmentCounter += 1

			else:
				print(response["Parameter"])
		else:
			now = datetime.datetime.now()

			self.sensor.LED(True)
			captured = self.__capture_the_lights__()

			if captured:
				identify = self.sensor.security()
				if identify["ACK"]:
					currentDate = self.numberFormat(now.year) + "-" + self.numberFormat(now.month) + "-" + self.numberFormat(now.day)
					time = self.numberFormat(now.hour) + ":" + self.numberFormat(now.minute) + ":" + self.numberFormat(now.second)
					preparedPayLoad = '{ "command": "ATTENDANCE", "scannerId": "'+ str(identify["Parameter"]) +'", "dateTime": "'+ currentDate +'", "time": "' + time + '" }'
					self.socket.send(preparedPayLoad)
				else:
					print(identify["Parameter"])

			self.enrollmentCounter = 0
			self.enrollment = False
			self.cancelEnroll = False
