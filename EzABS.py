import websocket
import json
from GTMainV2 import App
import threading
import time
import uuid
import RPi.GPIO as GPIO

class EzABS:
	def  __init__(self):
		websocket.enableTrace(True)
		self.ws = websocket.WebSocketApp(
			"ws://192.168.0.100:8080", 
			on_message = self.on_message, 
			on_error = self.on_error, 
			on_close = self.on_close,
			header = {
				'type:sensor', 
				'mac_address:'+str(hex(uuid.getnode()))
		})

		self.app = App()

		self.ws.on_open = self.on_open
		self.terminator = False
		self.sth = []
		self.ctr = 0

		wss = threading.Thread(target=self.ws.run_forever)
		wss.start()

	def switch(self, index, args):

		if index is "NU_REG":
			return self.app.setEnrollment(args)
		elif index is "CU_REG":
			self.app.cancelEnroll = True
			return "Canceled"		

	def on_message(self, ws, message):
		print("Connected")
		request = json.loads(message)

		response = self.switch(request["cmd"], request)

		print(message)

	def on_error(self, ws, error):
		print(error)

	def on_close(self, ws):
		print("### Socket Closed ###")

	def on_open(self, ws):
		print("### Socket Open ###")

		GPIO.setmode(GPIO.BCM)
		PIN = 18
		GPIO.setup(PIN, GPIO.IN)
		GPIO.add_event_detect(PIN, GPIO.FALLING, callback=self.app.pressedFinger)

if __name__ == '__main__':
	EzABS()
