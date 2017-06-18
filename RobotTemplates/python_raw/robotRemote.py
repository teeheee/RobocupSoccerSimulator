from socket import socket
import numpy as np
import main as m


class robotRemote:
	def __init__(self, _id):
		sock = socket()
		sock.connect(('127.0.0.1', 9996))
		self.motors = np.zeros(4)
		self.bodensensoren = np.zeros(16)
		self.ball = np.zeros(2)
		self.id = _id
		self.pos = np.zeros(3)

	def run(self):
		for line in sock.makefile('r'):
			n = line.split(",",1)
			self.pos[0] = int(n[0])
			self.pos[1] = int(n[1])
			self.pos[2] = int(n[2])
			self.ball[0] = int(n[3])
			self.ball[1] = int(n[4])
			for i in range(16):
				self.bodensensoren[i] = int(n(5+i))
			sock.send


if __name__ == "__main__" :
	rr = robotRemote(1)
	while True:
		rr.run()
		m.mainFunc(rr)
