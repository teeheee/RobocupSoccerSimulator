import numpy as np
import threading
import SocketServer
import subprocess


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):

	def handle(self):
		print "robot joined"
		while(True):
			if self.server.off:
				dline = self.rfile.readline()
				print "server recv:" + dline
				recvlist = [x.strip() for x in dline.split(',')]
				if len(recvlist) is not 5:
					print "server: wrong package length"
					break
				robotid = int(recvlist[0])
				if robotid < 1 or robotid > 4:
					print "server: wrong robot id"
					break
				robot = self.server.robots[robotid-1]
				robot.motorSpeed(float(recvlist[1]),
								float(recvlist[2]),
								float(recvlist[3]),
								float(recvlist[4]))
				ball = self.server.ball
				field = self.server.field
				points = field.getIntersectingPoints(robot)
				bodensensor = np.zeros(16)
				for p in points:
					bodensensor[int(np.degrees(np.arctan2(p[0], p[1]))*16/360)] = 1
				response = str(robot.pos[0]) + "," + \
							str(robot.pos[1]) + "," + \
							str(robot.pos[2]) + "," + \
							str(ball.pos[0]) + "," + \
							str(ball.pos[1])
				for s in bodensensor:
					response += ","+str(s)
				print "server send:" + response
				self.wfile.write(response)
			else:
				break
		print "thread shutting down" + str(threading.current_thread())


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	allow_reuse_address = True

	def addstuff(self, _robots, _ball, _field):
		self.robots = _robots
		self.ball = _ball
		self.field = _field


class robot_interface_sockets:
	def __init__(self, robots, ball, field):
		# Port 0 means to select an arbitrary unused port
		HOST, PORT = "localhost", 9996

		self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
		ip, port = self.server.server_address
		self.server.addstuff(robots, ball, field)
		self.server.off = True

		# Start a thread with the server -- that thread will then start one
		# more thread for each request
		server_thread = threading.Thread(target=self.server.serve_forever)
		# Exit the server thread when the main thread terminates
		server_thread.daemon = True
		server_thread.start()

		self.processes = list()

	def startRobot(self, robotpath, _id):
		args = ["python", robotpath, str(_id)]
		self.processes.append(subprocess.Popen(args))

	def shutdown(self):
		for p in self.processes:
			p.terminate()
			p.wait()
		self.server.off = False
		self.server.server_close()
		print "server shutting down"
		self.server.shutdown()










### test interface... needs to be overcome :-D


class robot_interface:
	def __init__(self,_game,_robot,_spielrichtung):
		self.robot = _robot
		self.game = _game
		self.spielrichtung = _spielrichtung
		self.robot.motor = np.array([0,0,0,0])
		self.bodensensor = np.zeros(16)
		self.timout = 0
		self.motor = np.array([0,0,0,0])

	def getData(self):
		self.richtung = (np.degrees(self.robot.pos[2])+self.spielrichtung) % 360
		if self.spielrichtung == 180:
			self.position = np.array([-self.robot.pos[0],-self.robot.pos[1]])
		else:
			self.position = np.array([self.robot.pos[0],self.robot.pos[1]])

		self.bodensensor = np.zeros(16)

		points = self.game.field.getIntersectingPoints(self.robot)
		for p in points:
			self.bodensensor[int(np.degrees(np.arctan2(p[0],p[1]))*16/360)] = 1

	def tick(self):
		self.getData()

		points = self.game.field.getIntersectingPoints(self.robot)
		if len(points) > 0:
			richtung = (self.richtung+180) % 360-180
			drall = -0.005*richtung
			d = self.position
			distanz = np.linalg.norm(d)
			d = d/distanz
			self.robot.motorSpeed(-d[0]+drall,-d[1]+drall,d[0]+drall,d[1]+drall)
			return

		ball = self.game.ball

		if self.spielrichtung == 180:
			ballposition = (-ball.pos[0],-ball.pos[1])
		else:
			ballposition = ball.pos

		d = np.array(ballposition-self.position)
		distanz = np.linalg.norm(d)
		d = d/distanz
		richtung = (self.richtung+180) % 360-180
		drall = -0.005*richtung
		ballrichtung = np.degrees(np.arctan2(d[0],d[1]))
		if (ballrichtung > 80 and ballrichtung < 100) or distanz > 25:
			self.robot.motorSpeed(d[0]+drall,d[1]+drall,-d[0]+drall,-d[1]+drall) 	# to the ball
		elif ballrichtung > 270 or ballrichtung < 80:
			self.robot.motorSpeed(-d[1]+drall,d[0]+drall,+d[1]+drall,-d[0]+drall) 	# around the ball
		else:
			self.robot.motorSpeed(+d[1]+drall,-d[0]+drall,-d[1]+drall,+d[0]+drall) 	# around the ball
