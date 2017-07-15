import socket
import numpy as np
import main as m
import sys
from time import sleep



class robotRemote:
	def __init__(self, _id):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect(('127.0.0.1', 9996))
		self.motors = np.zeros(4)
		self.bodensensoren = np.zeros(16)
		self.ball = np.zeros(2)
		self.id = _id
		self.pos = np.zeros(3)

	def run(self):
		sendpack = str(self.id) + "," +\
					str(self.motors[0]) + "," + str(self.motors[1]) + "," +\
					str(self.motors[2]) + "," + str(self.motors[3]) + "\r\n"
		self.sock.sendall(sendpack)
		print("robot"+str(self.id)+" sendet: " + sendpack)
		for line in self.sock.makefile('r'):
			print("robot"+str(self.id)+" recv: " + line)
			n = line.split(",", 1)
			self.pos[0] = float(n[0])
			self.pos[1] = float(n[1])
			self.pos[2] = float(n[2])
			self.ball[0] = float(n[3])
			self.ball[1] = float(n[4])
			for i in range(16):
				self.bodensensoren[i] = int(n(5+i))


if __name__ == "__main__":
	_id = int(sys.argv[1])
	if _id < 1 or _id > 4:
		print(str(_id) + " is a wrong ID! choose from 1,2,3,4!")
	rr = robotRemote(_id)
	while True:
		rr.run()
		m.mainFunc(rr)
