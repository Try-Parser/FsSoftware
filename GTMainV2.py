from GTSensor import GTSensor
from GTEnum import GT521F5
from time import sleep 
import base64
import json
import threading
import RPi.GPIO as GPIO

class App:
	def __init__(self):
		self.sensor = GTSensor('/dev/ttyAMA0', timeout=2, baudrate=9600)

		print ("Setting baudrate from 9600 to 57600")
		baudrateResult = self.sensor.setBaudrate(57600)
		print ("baudrate :" + str(baudrateResult));
		print ("Setting is done testing for LED lights")
		self.sensor.LED(True)
		sleep(1)
		self.sensor.LED(False)

	def getId(self):
		id = 0;

		while True and id <= 2999 :
			resp = self.sensor.checkEnrolled(id)
			print(resp);

			if GT521F5.ERRORS.value[resp["Parameter"]] is not 'NACK_IS_NOT_USED':
				break
			

	def enroll(self, id, ws):
		confirmation = self.sensor.startEnrollment()

	def pressedFinger(self):
		self.sensor.LED(True)
		sleep(1)
		self.sensor.LED(False)


if __name__ == '__main__':
	app = App()

	GPIO.setmode(GPIO.BCM)
	PIN = 18

	GPIO.setup(PIN, GPIO.IN)

	GPIO.add_event_detect(PIN, GPIO.FALLING, callback=app.pressedFinger);

	while True:
		print('AFK')
		sleep(1)

