import numpy as np


class robot_interface:
	def __init__(self,_robot):
		self.robot = _robot
		self.robot.motor = np.array([0,0,0,0])

	def getData(self):
		self.richtung = np.degrees(self.robot.body.angle)
		self.position = np.array([self.robot.body.position.x,self.robot.body.position.y])

	def tick(self, ball):
		self.getData()
		ballposition = np.array([ball.body.position.x,ball.body.position.y])

		d = np.array(ballposition-self.position)
		d = d/np.linalg.norm(d)
		a = (self.richtung+180) % 360-180
		a = -0.005*a
		self.robot.motor = np.array([d[0]+a,d[1]+a,-d[0]+a,-d[1]+a])
