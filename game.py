import numpy as np
import gameconfig as gc
from bot import *
from pymunk import *
import pymunk


class Robot:
	def __init__(self,_robotgrafik):
		self.robotgrafik = _robotgrafik
		self.radius = 10
		self.mass = 2000
		self.vmax = 10
		self.fmax = 10
		self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius, (0,0)))
		self.body.position = ((self.robotgrafik.x_position,self.robotgrafik.y_position))
		self.body.angle = np.radians(self.robotgrafik.orientation)
		self.shape = pymunk.Circle(self.body, self.radius, (0,0))
		self.shape.elasticity = 0
		self.shape.friction = 0.9
		self.motor = np.array([0,0,0,0])
		self.defekt = False

	def motorSpeed(self,a,b,c,d):
		self.motor = np.array([a,b,c,d])

	def tick(self):
		if self.defekt:
			self.robotgrafik.moveto(1000,1000,0)
			return
		self.robotgrafik.moveto((self.body.position.x),(self.body.position.y),-np.degrees(self.body.angle))

		A = np.array([[1, 0, -1, 0],[0, 1, 0, -1],[10, 10, 10, 10]])
		f = A.dot(self.motor)*10
		theta = self.body.angle
		c, s = np.cos(theta), np.sin(theta)
		R = np.array([[c, -s , 0], [s, c, 0], [0, 0, 1]])
		v = np.array([self.body.velocity[0],self.body.velocity[1],self.body.angular_velocity])
		f = R.dot(f)
		f_soll = (f-(self.fmax/self.vmax)*v)
		self.body.torque = f_soll[2]
		self.body.force = tuple(f_soll[0:2])


class Ball:
	def __init__(self,_ballgrafik):
		self.ballgrafik = _ballgrafik
		self.pos = np.array((self.ballgrafik.x_position,self.ballgrafik.y_position))
		self.f = np.array((0,0,0))
		self.radius = 3
		self.mass = 80
		self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius, (0,0)))
		self.body.position = ((self.ballgrafik.x_position,self.ballgrafik.y_position))
		self.shape = pymunk.Circle(self.body, self.radius, (0,0))
		self.shape.elasticity = 0.95
		self.shape.friction = 1

	def tick(self):
		self.ballgrafik.moveto((self.body.position.x),(self.body.position.y))


class Game:
	def __init__(self,_ball,_robots):
		self.ball = _ball
		self.robots = _robots
		self.space = pymunk.Space()
		self.space.damping = 0.995
		#Walls
		static_body = self.space.static_body
		static_lines = [pymunk.Segment(static_body, (-gc.OUTER_FIELD_LENGTH/2, -gc.OUTER_FIELD_WIDTH/2), (-gc.OUTER_FIELD_LENGTH/2, gc.OUTER_FIELD_WIDTH/2), 0.0)
		                ,pymunk.Segment(static_body, (-gc.OUTER_FIELD_LENGTH/2, -gc.OUTER_FIELD_WIDTH/2), (gc.OUTER_FIELD_LENGTH/2, -gc.OUTER_FIELD_WIDTH/2), 0.0)
		                ,pymunk.Segment(static_body, (gc.OUTER_FIELD_LENGTH/2, gc.OUTER_FIELD_WIDTH/2), (-gc.OUTER_FIELD_LENGTH/2, gc.OUTER_FIELD_WIDTH/2), 0.0)
		                ,pymunk.Segment(static_body, (gc.OUTER_FIELD_LENGTH/2, gc.OUTER_FIELD_WIDTH/2), (gc.OUTER_FIELD_LENGTH/2, -gc.OUTER_FIELD_WIDTH/2), 0.0)]
		for line in static_lines:
		    line.elasticity = 0.95
		    line.friction = 0.9
		self.space.add(static_lines)

		#Goal
		static_body = self.space.static_body
		static_lines2 = [pymunk.Segment(static_body, (gc.INNER_FIELD_LENGTH/2, -gc.GOAL_WIDTH/2) 			   , (gc.INNER_FIELD_LENGTH/2, gc.GOAL_WIDTH/2), 0.0)
						,pymunk.Segment(static_body, (gc.INNER_FIELD_LENGTH/2, gc.GOAL_WIDTH/2) 			   , (gc.INNER_FIELD_LENGTH/2+gc.GOAL_DEEP, gc.GOAL_WIDTH/2),0.0)
						,pymunk.Segment(static_body, (gc.INNER_FIELD_LENGTH/2 + gc.GOAL_DEEP, gc.GOAL_WIDTH/2) , (gc.INNER_FIELD_LENGTH/2+gc.GOAL_DEEP, -gc.GOAL_WIDTH/2),0.0)
						,pymunk.Segment(static_body, (gc.INNER_FIELD_LENGTH/2 + gc.GOAL_DEEP, -gc.GOAL_WIDTH/2), (gc.INNER_FIELD_LENGTH/2, -gc.GOAL_WIDTH/2),0.0)
						,pymunk.Segment(static_body, (-gc.INNER_FIELD_LENGTH/2, -gc.GOAL_WIDTH/2) 			   , (-gc.INNER_FIELD_LENGTH/2, gc.GOAL_WIDTH/2), 0.0)
						,pymunk.Segment(static_body, (-gc.INNER_FIELD_LENGTH/2, gc.GOAL_WIDTH/2) 			   , (-gc.INNER_FIELD_LENGTH/2-gc.GOAL_DEEP, gc.GOAL_WIDTH/2),0.0)
						,pymunk.Segment(static_body, (-gc.INNER_FIELD_LENGTH/2-gc.GOAL_DEEP, gc.GOAL_WIDTH/2)  , (-gc.INNER_FIELD_LENGTH/2-gc.GOAL_DEEP, -gc.GOAL_WIDTH/2),0.0)
						,pymunk.Segment(static_body, (-gc.INNER_FIELD_LENGTH/2-gc.GOAL_DEEP, -gc.GOAL_WIDTH/2) , (-gc.INNER_FIELD_LENGTH/2, -gc.GOAL_WIDTH/2),0.0)]
		for line in static_lines2:
		    line.elasticity = 0.95
		    line.friction = 0.9
		self.space.add(static_lines2)

		#Robots
		for robot in self.robots:
			self.space.add(robot.body,robot.shape)
		#Ball
		self.space.add(self.ball.body,self.ball.shape)

		#Robot interface
		self.ris = [robot_interface(self.robots[0]),robot_interface(self.robots[1]),robot_interface(self.robots[2]),robot_interface(self.robots[3])]

	def tick(self,dt):
		self.space.step(dt)
		self.ball.tick()
		for robot in self.robots:
			robot.tick()
			self.isOutOfBounce(robot)
		for ri in self.ris[1:4]:
			ri.tick(self.ball)

	def isOutOfBounce(self,robot):
		if robot.body.position.x > (gc.INNER_FIELD_LENGTH/2+robot.radius*2):
			robot.defekt = True
		if robot.body.position.x < -(gc.INNER_FIELD_LENGTH/2+robot.radius*2):
			robot.defekt = True
		if robot.body.position.y > (gc.INNER_FIELD_WIDTH/2+robot.radius*2):
			robot.defekt = True
		if robot.body.position.y < -(gc.INNER_FIELD_WIDTH/2+robot.radius*2):
			robot.defekt = True
