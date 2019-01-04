import websocket
import json
from GTMainV2 import App
import threading
import time
import uuid
import RPi.GPIO as GPIO
import base64
import yaml

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
		elif cmd == "DELETE_TEMP":
			self.app.deleteSingleTemplate(args["scannerId"])
		elif cmd == "S_TEMPLATE":
			if args["message"] == "Templates":
				body = args["body"]
				if not body["empty"]:
					content = body["content"][0]
					response = self.app.saveTemplate(base64.b64decode(content["print"].encode()), content["scannerId"])
					if response == "successful":
						success = True
						code = 102
					else:
						success = False
						code = 906
					preparedPayload = '{ "command": "SENSOR_STATUS", "mac_address": "'+ str(hex(uuid.getnode()))+'", "success": "' +str(success)+'", "message": "'+ response +'", "code": "'+ str(code) +'" }'
					self.ws.send(preparedPayload)
		else:
			print("WTF")

	def reset(self): 
		print("Im heere")
		self.app.clearDb()
		self.ws.send('{ "command": "TP_RESET" }')

	def on_message(self, ws, message):
		print("Connected")
		print(message)

		request = json.loads(message)

		if "cmd" not in request:
			requestCmd = "S_TEMPLATE"
		else:
			requestCmd = request["cmd"]

		self.switch(requestCmd, request)

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
