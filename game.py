import numpy as np
import gameconfig as gc
from interface import *
from grafik import *
from physik import *
from pymunk import *
import pymunk


class Robot:
	def __init__(self,display, space,_id,color):
		self.grafik = RobotGrafik(display,_id,color)
		self.physik = RobotPhysik(space,self.grafik)
		self.id = _id
		self.pos = np.array([0,0,0])
		self.radius = self.physik.radius

	#setzt den Roboter in Zustand Defekt und platziert ihn weit weg (kann nur einmal aufgerufen werden. Danach muss der timeout ablaufen)
	def defekt(self,time):
		if self.physik.defekt:
			return
		self.defektTime = time
		self.physik.defekt = True
		self.moveto(10000,self.id*10000,0)

	#testet ob der Roboter nicht mehr defekt ist. (timeout vorbei)
	def isDefekt(self,time):
		if self.physik.defekt:
			if time-self.defektTime > 2000:
				self.physik.defekt = False
				return False
		return True

	#setzt den Motorspeed
	def motorSpeed(self,a,b,c,d):
		self.physik.motorSpeed(a,b,c,d)

	#bewegt den Roboter an Position x,y mit der richtung d
	def moveto(self,x,y,d):
		self.physik.moveto(x,y,d)
		self.grafik.moveto(x,y,d)

	#Spieltick wird ausgefuehrt. Roboter Position wird aktualisiert
	def tick(self):
		self.physik.tick()
		self.pos = np.array([self.physik.body.position.x,self.physik.body.position.y,self.physik.body.angle])

	#Zeichnet den Roboter
	def draw(self):
		self.grafik.draw()

	#gibt True zurueck wenn der Roboter von diesem Object beruehrt wird
	def isPushedBy(self,  _object):
		return self.physik.isPushedBy(_object.physik)

	#gibt True zurueck wenn der Roboter nicht mehr im Spielfeld ist
	def isOutOfBounce(self):
		if self.pos[0] > (gc.INNER_FIELD_LENGTH/2+self.radius) or\
			   self.pos[0] < -(gc.INNER_FIELD_LENGTH/2+self.radius) or\
			   self.pos[1] > (gc.INNER_FIELD_WIDTH/2+self.radius) or\
			   self.pos[1] < -(gc.INNER_FIELD_WIDTH/2+self.radius):
			return True
		return False

	def isInStrafraum(self, seite):
		if seite is "links":
			if self.pos[0] > -20+gc.INNER_FIELD_LENGTH/2 and\
				self.pos[0] < +gc.INNER_FIELD_LENGTH/2 and\
				self.pos[1] > -45 and\
				self.pos[1] < 45:
				return True
			return False
		if seite is "rechts":
			if self.pos[0] < +20-gc.INNER_FIELD_LENGTH/2 and\
				self.pos[0] > -gc.INNER_FIELD_LENGTH/2 and\
				self.pos[1] > -45 and\
				self.pos[1] < 45:
				return True
			return False


class Ball:
	def __init__(self,display,space):
		self.grafik = BallGrafik(display)
		self.physik = BallPhysik(space,self.grafik)
		self.pos = np.array(self.physik.body.position)

	#Spieltick wird ausgefuerht
	def tick(self):
		self.physik.tick()
		self.pos = np.array(self.physik.body.position)

    #Setzt den Ball an Position x,y
	def moveto(self,x,y):
		self.physik.moveto(x,y)
		self.grafik.moveto(x,y)

    #Ball zeichnen
	def draw(self):
		self.grafik.draw()

    #Gibt True zurueck wenn der Ball sich bewegt Threshold ist 0.01. kann man noch anpassen
	def isMoving(self):
		return np.linalg.norm(self.physik.body.velocity) > 0.02


class Field:
	def __init__(self,display,space):
		self.grafik = FeldGrafik(display)
		self.physik = FieldPhysik(space)

	#Wegen Kompatibilitaet?
	def tick(self):
		pass

	#Feld Zeichnen
	def draw(self):
		self.grafik.draw()

	#Spielstand updaten
	def setSpielstand(self, a, b):
		self.grafik.setSpielstand(a,b)

	#gibt alle Schnittpunkte des Roboters robot mit der Auslinien relativ zum Roboter wieder
	def getIntersectingPoints(self, robot):
		return self.physik.getIntersectingPoints(robot.physik)


class NeutralSpot:
	def __init__(self,_pos):
		self.pos = _pos

	#gibt die Distanz von dem objekt (ball oder roboter) zu dem neutralen Punkt
	def distance(self,object):
		return np.linalg.norm(self.pos-object.pos[0:2])

	#gibt True zurueck wenn einer der roboter in robots oder der ball den neutralen Punkt besetzen
	def isOccupied(self,robots,ball):
		for robot in robots:
			d = np.linalg.norm(robot.pos[0:2]-self.pos)
			if d < 30:
				print "occupied by robot"
				return True
		d = np.linalg.norm(ball.pos[0:2]-self.pos)
		if d < 20:
			print "occupied by ball"
			return True
		return False


class Game:
	def __init__(self,_display):
		self.spielstand = [0,0]
		self.isgoal = False
		self.autopilot = True

		self.time = 0
		self.balltimeout = 0
		self.display = _display

		self.space = pymunk.Space()
		self.space.damping = 0.995

		self.field = Field(self.display,self.space)

		self.ball = Ball(self.display,self.space)

		BLUE = 0,0,255
		RED = 255,0,0

		self.robots = [Robot(self.display,self.space,1,BLUE),
					   Robot(self.display,self.space,2,BLUE),
					   Robot(self.display,self.space,3,RED),
					   Robot(self.display,self.space,4,RED)]

		# Todo flexible starting Position
		self.robots[0].moveto(13,1,180)
		self.robots[1].moveto(80,-1,180)
		self.robots[2].moveto(-40,3,0)
		self.robots[3].moveto(-80,2,0)

		self.nspots = [NeutralSpot((gc.INNER_FIELD_LENGTH/2-45,gc.GOAL_WIDTH/2)),
					   NeutralSpot((gc.INNER_FIELD_LENGTH/2-45,-gc.GOAL_WIDTH/2)),
					   NeutralSpot((-gc.INNER_FIELD_LENGTH/2+45,gc.GOAL_WIDTH/2)),
					   NeutralSpot((-gc.INNER_FIELD_LENGTH/2+45,-gc.GOAL_WIDTH/2)),
					   NeutralSpot((0,0))]

		#Robot interface
		if self.autopilot:
			self.ris = [robot_interface(self,self.robots[0],180),
						robot_interface(self,self.robots[1],180),
						robot_interface(self,self.robots[2],0),
						robot_interface(self,self.robots[3],0)]

		self.robotinterface = robot_interface_sockets(self.robots,self.ball,self.field)

	def tick(self,dt):
		self.time += dt 											# Sielzeit hochzaelen
		self.space.step(dt) 										# Physik engine einen Tick weiter laufen lassen
		self.ball.tick()								 			# Ball updaten
		for robot in self.robots:
			robot.tick() 											# Roboter updaten
			self.isOutOfBounce(robot) 								# roboter auf OutofBounce testen
			if robot.isDefekt(self.time) is False: 					# roboter auf nicht mehr defekt testen TODO kann man schoner machen
				self.setzteRobotaufNeutralenPunkt(robot)

		self.lagofProgress()  										# Lag of Progress testen
		self.checkGoal()     										# Tor testen
		self.doubleDefense()  										# check double defense
		self.pushing()												# check for pushing
		if self.isgoal: 											# TODO kann man schoener machen (startposition variabel?)
			for robot in self.robots:
				robot.physik.defekt = False
			self.robots[0].moveto(13,1,180)
			self.robots[1].moveto(80,-1,180)
			self.robots[2].moveto(-40,1,0)
			self.robots[3].moveto(-80,-1,0)
			self.ball.moveto(0,0) 									# Ball in die Mitte legen
			self.isgoal = False

		if self.autopilot:
			for ri in self.ris[0:4]:
				ri.tick() 											# Roboter program laufen lassen

	def draw(self):
		self.field.draw()
		self.ball.draw()
		for robot in self.robots:
			robot.draw()

	def shutdown(self):
		self.robotinterface.shutdown()

	def setzteBallaufNeutralenPunkt(self):
		bestspot = self.nspots[0]
		for nspot in self.nspots:
			if nspot.distance(self.ball) < bestspot.distance(self.ball) and not nspot.isOccupied(self.robots,self.ball):
				bestspot = nspot
		pos = bestspot.pos
		self.ball.moveto(pos[0],pos[1])

	def setzteRobotaufNeutralenPunkt(self,robot):
		bestspot = self.nspots[0]
		for nspot in self.nspots:
			if nspot.distance(robot) < bestspot.distance(robot) and not nspot.isOccupied(self.robots,self.ball):
				bestspot = nspot
		pos = bestspot.pos
		robot.moveto(pos[0],pos[1],robot.pos[2])

	def setzteRobotwiederinsSpiel(self,robot):
		bestspot = self.nspots[0]
		for nspot in self.nspots:
			if nspot.distance(self.ball) > bestspot.distance(self.ball) and not nspot.isOccupied(self.robots,self.ball):
				bestspot = nspot
		pos = bestspot.pos
		robot.moveto(pos[0],pos[1],0)

	def lagofProgress(self):
		if self.ball.isMoving():
			self.balltimeout = self.time
		if self.time-self.balltimeout > 2000:
			print "lag of progress!!!"
			self.setzteBallaufNeutralenPunkt()
			self.balltimeout = self.time

	def isOutOfBounce(self,robot):
		if robot.isOutOfBounce():
		   	for otherrobot in self.robots:
		   		if robot.isPushedBy(otherrobot) and otherrobot is not robot:
		   			print "pushed out!!!"
		   			self.setzteRobotaufNeutralenPunkt(robot)
		   			return
		   	print "out of bounce!!!"
			robot.defekt(self.time)

	def pushing(self):
		for i in range(0,2):
			if self.robots[i].isInStrafraum("links"):
				if self.robots[i].isPushedBy(self.robots[2]):
					if self.robots[i].isPushedBy(self.ball) or self.robots[2].isPushedBy(self.ball):
						print "pushing!!!"
						self.setzteBallaufNeutralenPunkt()
				if self.robots[i].isPushedBy(self.robots[3]):
					if self.robots[i].isPushedBy(self.ball) or self.robots[3].isPushedBy(self.ball):
						print "pushing!!!"
						self.setzteBallaufNeutralenPunkt()

		for i in range(2,4):
			if self.robots[i].isInStrafraum("rechts"):
				if self.robots[i].isPushedBy(self.robots[0]):
					if self.robots[i].isPushedBy(self.ball) or self.robots[0].isPushedBy(self.ball):
						print "pushing!!!"
						self.setzteBallaufNeutralenPunkt()
				if self.robots[i].isPushedBy(self.robots[1]):
					if self.robots[i].isPushedBy(self.ball) or self.robots[1].isPushedBy(self.ball):
						print "pushing!!!"
						self.setzteBallaufNeutralenPunkt()

	def doubleDefense(self):
		if self.robots[0].isInStrafraum("links") and\
		   self.robots[1].isInStrafraum("links"):
			d1 = np.linalg.norm(self.robots[0].pos[0:2]-self.ball.pos)
			d2 = np.linalg.norm(self.robots[1].pos[0:2]-self.ball.pos)
			print "double defense!!!"
			if d1 > d2:
				self.setzteRobotaufNeutralenPunkt(self.robots[0])
			else:
				self.setzteRobotaufNeutralenPunkt(self.robots[1])

		if self.robots[2].isInStrafraum("rechts") and\
		   self.robots[3].isInStrafraum("rechts"):
			d1 = np.linalg.norm(self.robots[2].pos[0:2]-self.ball.pos)
			d2 = np.linalg.norm(self.robots[3].pos[0:2]-self.ball.pos)
			print "double defense!!!"
			if d1 > d2:
				self.setzteRobotaufNeutralenPunkt(self.robots[2])
			else:
				self.setzteRobotaufNeutralenPunkt(self.robots[3])

	def checkGoal(self):
		if self.ball.pos[0] < -gc.INNER_FIELD_LENGTH/2 and self.ball.pos[0] > -gc.INNER_FIELD_LENGTH/2-gc.GOAL_DEEP and self.ball.pos[1] > -gc.GOAL_WIDTH/2 and self.ball.pos[1] < gc.GOAL_WIDTH/2:
		   	self.spielstand[0] = self.spielstand[0]+1
		   	print "GOAL"
		   	self.isgoal = True

		if self.ball.pos[0] > gc.INNER_FIELD_LENGTH/2 and self.ball.pos[0] < gc.INNER_FIELD_LENGTH/2+gc.GOAL_DEEP and self.ball.pos[1] > -gc.GOAL_WIDTH/2 and self.ball.pos[1] < gc.GOAL_WIDTH/2:
		   	self.spielstand[1] = self.spielstand[1]+1
		   	print "GOAL"
		   	self.isgoal = True

		self.field.setSpielstand(self.spielstand[1],self.spielstand[0])
