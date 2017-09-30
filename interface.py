import numpy as np
import random
import gameconfig as gc
import pymunk
from enum import Enum

class State(Enum):
    Active = 0
    Defekt = 1
    Running = 2
    OutOfBounce = 3
    OwnGoal = 4
    OponentGoal = 5
    MultipleDefence = 6
    LagOfProgress = 7


class Interface:
    def __init__(self, game, id):
        self._robot = game.robots[id]
        self._id = id
        self._game = game
        self._playDirection = self._robot.playDirection
        self._body = self._robot.physik.body
        self._space = self._robot.physik.space

    # Returns a list of 16 Analog Sensor Values representing Black and White and Green lines
    # Numbering starts at the front and goes clockwise
    def getLineSensors(self):
        bodensensor = np.zeros(16)
        points = []
        for line in self._game.field.physik.outLine:
            A = np.array(line.a)
            B = np.array(line.b)
            C = np.array(self._robot.body.position)
            R = 8

            LAB = np.linalg.norm(A - B)
            D = (B - A) / LAB
            t = D * (C - A)
            E = t * D + A
            LEC = np.linalg.norm(E - C)

            if LEC < R:
                dt = np.sqrt(R - LEC)
                F = (t - dt) * D + A
                G = (t + dt) * D + A
                points.append(F - C)
                points.append(G - C)
            elif LEC == R:
                points.append(E - C)
        i=0
        for p in points:
            p = p / 4
            w = np.rad2deg(np.arctan2(p[0], p[1]))
            winkel = 360-(w+self._robot.orientation+270)%360
            i+=1
            index = int(winkel * 16 / 360)%16
            bodensensor[index] = 1
            # sometimes multiple sensors detect the ball ;-)
            if random.randrange(100) < 50:
                bodensensor[(index+1)%16] = 1
            if random.randrange(100) < 50:
                bodensensor[(index+15)%16] = 1
        return bodensensor

    # Returns a list of 4 Distance measurements in all 4 directions
    # Numbering starts at the front and goes clockwise
    def getUltrasonic(self):
        usValue = np.array([0, 0, 0, 0])
        filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0x1)  # this is some pymunk voodoo
        queryList = list()
        radians = self._body.angle
        rotationMatrix = np.array([(np.cos(radians), -np.sin(radians)),
                                    (np.sin(radians), np.cos(radians))])
        v1 = np.matmul(rotationMatrix, np.array([200, 0]))
        v2 = np.matmul(rotationMatrix, np.array([0, 200]))
        v3 = np.matmul(rotationMatrix, np.array([-200, 0]))
        v4 = np.matmul(rotationMatrix, np.array([0, -200]))
        queryList.append(self._space.segment_query(self._body.position, self._body.position + v1, 5, filter))
        queryList.append(self._space.segment_query(self._body.position, self._body.position + v2, 5, filter))
        queryList.append(self._space.segment_query(self._body.position, self._body.position + v3, 5, filter))
        queryList.append(self._space.segment_query(self._body.position, self._body.position + v4, 5, filter))
        i = 0
        for query in queryList:
            finalReflectionDistance = 200
            for singleQuery in query:
                dotOfInterest = singleQuery.point
                distanceToDotOfInterest = np.linalg.norm(dotOfInterest - self._body.position)
                if distanceToDotOfInterest < finalReflectionDistance:
                    finalReflectionDistance = distanceToDotOfInterest
            usValue[i] = finalReflectionDistance - 10  # subtract radius of robot
            if usValue[i] <= 0:
                usValue[i] = 200
            i = i + 1
            return usValue

    # Returns a List of Blocks of detected Objects
    # Attributes of each object is signature, x and y Position in camera vision
    # 1 is Ball
    # 2 is own Goal
    # 3 is opponent Goal
    # 4-9 are the Landmarks
    def getPixy(self):  # TODO pixy is not implemented
        pass

    # Returns a list of 16 IR sensors. Value corresponds to distance from the Ball
    # Numbering starts at the front and goes clockwise
    def getIRBall(self):
        irsensors = np.zeros(16)
        ball_relative_robot = np.subtract(self._game.ball.pos,self._robot.pos[0:2])
        distanz = np.linalg.norm(ball_relative_robot)
        ballrichtung = (np.degrees(np.arctan2(ball_relative_robot[0], ball_relative_robot[1])) + random.gauss(0,5) + 270) % 360
        ballrichtung = (ballrichtung + self._robot.orientation)%360
        ballrichtung = 360-ballrichtung
        if distanz > 0:
            index = int(ballrichtung * 16 / 360)%16
            irsensors[index] = int(1000/distanz)
           #irsensors[(index+1)%16] = int(300/distanz)
            #irsensors[(index+15)%16] = int(300/distanz)
            #irsensors[(index+2)%16] = int(30/distanz)
            #irsensors[(index+14)%16] = int(30/distanz)
        return irsensors

    # Returns the orientation of the Robot in degree. 180° is opponent goal. Numbering goes clockwise
    def getKompass(self):
        kompass = (np.degrees(self._robot.pos[2]) + self.spielrichtung + 180) % 360
        return int(kompass + random.gauss(0, 1))

    # sets the motor speeds to this value motors rotate the robot counter clockwise.
    # numbering starts at the front and goes clockwise
    def setMotorSpeed(self,m0,m1,m2,m3):
        m0 = m0 * random.gauss(1,0.02)
        m1 = m1 * random.gauss(1,0.02)
        m2 = m2 * random.gauss(1,0.02)
        if m0 > 100:
            m0 = 100
        if m0 < -100:
            m0 = -100
        m0 = m0/100
        if m1 > 100:
            m1 = 100
        if m1 < -100:
            m1 = -100
        m1 = m1/100
        if m2 > 100:
            m2 = 100
        if m2 < -100:
            m2 = -100
        m2 = m2/100
        if m3 > 100:
            m3 = 100
        if m3 < -100:
            m3 = -100
        m3 = m3/100
        self._robot.motorSpeed(m0, m1, m2, m3)

    # toggles the kicker
    def Kick(self):
        if self.getLightBarrier():
            self._game.ball.kick(self._robot.orientation)

    # detects the ball in the ball capture zone
    def getLightBarrier(self):
        BallVektor = self._robot.pos[0:2] - self._game.ball.pos
        theta = np.deg2rad(self._robot.orientation)
        c,s = np.cos(theta),np.sin(theta)
        rotMatrix = np.array([[c, s],[-s, c]])
        relativBallVektor = np.dot(rotMatrix,BallVektor)
        if relativBallVektor[0] > -11 and relativBallVektor[0] < 0:
            if np.abs(relativBallVektor[1]) < 3:
                return True
        return False

    # See class State(Enum) for diffrent states
    def getRobotState(self):
        if self._game.wasGoal():
            if self._robot.id <= 1:
                if self._game.lastgoalteam == 1:
                    return State.OwnGoal
                else:
                    return State.OponentGoal
            else:
                if self._game.lastgoalteam == 2:
                    return State.OwnGoal
                else:
                    return State.OponentGoal
        elif self._robot.physik.defekt == True:
            return State.Defekt
        elif self._game.wasTimeout():
            return State.TimeOut
        else:
            return State.Active

    def restartGame(self):
        self._game.restart()