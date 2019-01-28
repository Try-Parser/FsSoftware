from GTSensor import GTSensor
from GTEnum import GT521F5
from time import sleep 
import base64
import json
import datetime
import uuid

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
	                if self.sensor.captureFinger(True)['ACK']:
	                        print ("Captured")
	                        self.sensor.LED(False)
	                        return True
	                else:
	                	self.Sensor.LED(False)
	                	return False
	        else:
	        	return False

	def switch(self, enrollmentIndex):
		if enrollmentIndex is 0:
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

	def deleteSingleTemplate(self, sensorId):
		response = self.sensor.rmById(int(sensorId))
		if response["ACK"]:
			success = True
			code = 101
		else:
			success = False
			code = 901
		preparedPayload = '{ "command": "SENSOR_STATUS", "mac_address": "'+ str(hex(uuid.getnode()))+'", "success": "' +str(success)+'", "message": "'+ str(response["Parameter"]) +'", "code": "'+ str(code) +'" }'
		self.socket.send(preparedPayload)

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
		print(self.enrollmentCounter)
		print(self.enrollment and self.enrollmentCounter <= 3)

		procced = False

		if self.enrollment and self.enrollmentCounter <= 3:

			if self.enrollmentCounter is 0:
				self.getId()
				print(self.enrollmentCandidate)
				response = self.switch(self.enrollmentCounter)
				if response["ACK"]:
					self.enrollmentCounter += 1
					procced = True
				else:
					preparedPayLoad = '{ "command": "SENSOR_STATUS", "mac_address": "'+ str(hex(uuid.getnode()))+'", "message": "'+ str(response["Parameter"]) +' Failed to register!", "success": "false", "code":"906" }'
					self.socket.send(preparedPayLoad)		
			else:
				procced = True	

			if procced:
				response = self.switch(self.enrollmentCounter)
				print(response)
				if response["ACK"]:
					self.sensor.LED(True)

					while not self.__capture_the_lights__():
						if self.cancelEnroll:
							break

					preparedPayLoad = '{ "command": "SENSOR_STATUS", "mac_address": "'+ str(hex(uuid.getnode()))+'", "message": "Step '+ str(self.enrollmentCounter)+ '" , "success": "true", "code":"104" }'
					self.socket.send(preparedPayLoad)

					self.enrollmentCounter += 1

					if self.enrollmentCounter is 4:
						templateResponse = self.switch(self.enrollmentCounter)
						if templateResponse[0]['ACK']:
							preparedPayLoad = '{ "command": "W_REGED", "template": "'+ base64.b64encode(templateResponse[1]['Data']).decode() +'", "userId":"'+str(self.userId)+'", "scannerId":'+str(self.enrollmentCandidate)+'}'
							self.socket.send(preparedPayLoad)
							print("payload send")
				elif not response["ACK"] and response["Parameter"] is 0:
					print("Fingerprint is used")
					self.enrollmentCounter += 1
					preparedPayLoad = '{ "command": "SENSOR_STATUS", "mac_address": "'+ str(hex(uuid.getnode()))+'", "message": "Fingerprint is in used.", "success": "false", "code":"902" }'
					self.socket.send(preparedPayLoad)
					self.enrollment = True
					self.enrollmentCounter = 0
				else:
					preparedPayLoad = '{ "command": "SENSOR_STATUS", "mac_address": "'+ str(hex(uuid.getnode()))+'", "message": "'+ str(response["Parameter"]) +' Sensor Error Restarting enrollment process.", "success": "false", "code":"903" }'
					self.socket.send(preparedPayLoad)
					self.enrollment = True
					self.enrollmentCounter = 0
					preparedPayLoad = '{ "command": "SENSOR_STATUS", "mac_address": "'+ str(hex(uuid.getnode()))+'", "message": "Enrollment starts from the begining.", "success": "false", "code":"904" }'
					self.socket.send(preparedPayLoad)
		else:
			now = datetime.datetime.now()
			preparedPayLoad = '{ "command": "SENSOR_STATUS", "mac_address": "'+ str(hex(uuid.getnode()))+'", "message": "Searching", "success": "true", "code":"103" }'
			self.socket.send(preparedPayLoad)
			self.sensor.LED(True)
			captured = self.__capture_the_lights__()

			if captured:
				identify = self.sensor.security()
				print(identify)
				if identify["ACK"]:
					currentDate = self.numberFormat(now.year) + "-" + self.numberFormat(now.month) + "-" + self.numberFormat(now.day)
					time = self.numberFormat(now.hour) + ":" + self.numberFormat(now.minute) + ":" + self.numberFormat(now.second)
					preparedPayLoad = '{ "command": "ATTENDANCE", "scannerId": "'+ str(identify["Parameter"]) +'", "dateTime": "'+ currentDate +'", "time": "' + time + '" }'
					self.socket.send(preparedPayLoad)
				else:
					if identify["Parameter"] == "NACK_IDENTIFY_FAILED":
						preparedPayLoad = '{ "command": "SENSOR_STATUS", "mac_address": "'+ str(hex(uuid.getnode()))+'", "success": "false", "message": "Unindentified finger", "code": "905" }'
						self.socket.send(preparedPayLoad)
					
					print(identify["Parameter"])

			self.enrollmentCounter = 0
			self.enrollment = False
			self.cancelEnroll = False
