from GTSensor import GTSensor
from GTEnum import GT521F5
import time
import base64
import json
import threading


class App:
	def __init__(self):
		self.sensor = GTSensor('/dev/ttyAMA0', timeout=2, baudrate=9600)

		print ("Setting baudrate from 9600 to 57600")
		baudrateResult = self.sensor.setBaudrate(57600)
		print ("baudrate :" + str(baudrateResult));
		print ("Setting is done testing for LED lights")
		self.sensor.LED(True)
		time.sleep(0.5)
		self.sensor.LED(False)

		self.getId();	

	def getId(self):
		id = 0;

		while True and id <= 2999 :
			resp = self.CheckEnrolled(id)
			print(resp);

			if GT521F5.ERRORSalue[check_id["Parameter"]] is 'NACK_IS_NOT_USED':
				break
			

	def enroll(self, id, ws):
		confirmation = self.sensor.startEnrollment()


if __name__ == '__main__':
	App()