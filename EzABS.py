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

	def switch(self, cmd, args) :
		if cmd == "NU_REG": 
			self.app.setEnrollment(args)
		elif cmd == "CU_REG":
			self.app.cancelEnrollment()
		elif cmd == "DB_RESET":
			self.reset()
		else:
			if args["message"] == "Templates":
				body = args["body"]
				if not body["empty"]:
					content = body["content"][0]
					print(content["scannerId"])
					print(ase64.b64decode(content["print"].encode()))
					# print(body["content"][0])
			print("WTF")

	def reset(self): 
		self.app.clearDb()
		self.ws.send('{ "cmd": "TP_RESET" }')

	def on_message(self, ws, message):
		print("Connected")
		request = json.loads(message)

		self.switch(request["cmd"], request)

		print(message)

	def on_error(self, ws, error):
		print(error)

	def on_close(self, ws):
		print("### Socket Closed ###")

	def on_open(self, ws):
		print("### Socket Open ###")
		self.app.setSocket(self.ws)
		GPIO.setmode(GPIO.BCM)
		PIN = 18
		GPIO.setup(PIN, GPIO.IN)
		GPIO.add_event_detect(PIN, GPIO.FALLING, callback=self.app.pressedFinger)


if __name__ == '__main__':
	EzABS()
