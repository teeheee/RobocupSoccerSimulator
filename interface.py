import numpy as np
import random
import gameconfig

class robot_interface:
    def __init__(self, _game, _robot, _spielrichtung):
        self.robot = _robot
        self.id = _robot.id
        self.game = _game
        self.spielrichtung = _spielrichtung
        self.motor = np.array([0, 0, 0, 0])

    # Returns a list of 16 Analog Sensor Values representing Black and White and Green lines
    # Numbering starts at the front and goes clockwise
    def getBodenSensors(self):
        bodensensor = np.zeros(16)
        points = self.game.field.getIntersectingPoints(self.robot)
        i=0
        for p in points:
            p = p / 4
            w = np.rad2deg(np.arctan2(p[0], p[1]))
            winkel = 360-(w+self.robot.orientation+270)%360
            i+=1
            bodensensor[int(winkel * 16 / 360)%16] = 1
        return bodensensor

    # Returns a list of 4 Distance measurements in all 4 directions
    # Numbering starts at the front and goes clockwise
    def getUltraschall(self): #TODO getUltraschall ist noch nicht fertig hindernisse fehlen
        return self.robot.getUS()



        if self.spielrichtung == 180:
            pos = np.array([int(-self.robot.pos[0]), int(-self.robot.pos[1])])
        else:
            pos = np.array([int(self.robot.pos[0]), int(self.robot.pos[1])])
        US = []
        US.append(np.absolute(int( -gameconfig.OUTER_FIELD_WIDTH/2 + gameconfig.OUTER_FIELD_WIDTH-pos[0]-10)))
        US.append(np.absolute(int( -gameconfig.OUTER_FIELD_LENGTH/2 + gameconfig.OUTER_FIELD_LENGTH-pos[1]-10 )))
        US.append(np.absolute(int( gameconfig.OUTER_FIELD_WIDTH/2 + pos[0]-10)))
        US.append(np.absolute(int( gameconfig.OUTER_FIELD_LENGTH/2 + pos[1]-10)))

        for u in US:
            u = int(u + random.gauss(0,5))
            if u > 200:
                u = 0
            if u < 5:
                u = 0

        return US

    # Returns a List of Blocks of detected Objects
    # Attributes of each object is signature, x and y Position in camera vision
    # 1 is Ball
    # 2 is own Goal
    # 3 is opponent Goal
    # 4-9 are the Landmarks
    def getPixy(self): #TODO getPixy ist noch nicht fertig
        pass

    # Returns a list of 16 IR sensors. Value corresponds to distance from the Ball
    # Numbering starts at the front and goes clockwise
    def getIRBall(self):
        irsensors = np.zeros(16)
        ball_relative_robot = np.subtract(self.game.ball.pos,self.robot.pos[0:2])
        distanz = np.linalg.norm(ball_relative_robot)
        ballrichtung = (np.degrees(np.arctan2(ball_relative_robot[0], ball_relative_robot[1])) + random.gauss(0,5) + 270) % 360
        ballrichtung = (ballrichtung + self.robot.orientation)%360
        ballrichtung = 360-ballrichtung
        if distanz > 0:
            irsensors[int(ballrichtung * 16 / 360)%16] = int(1000/distanz)
        return irsensors

    # Returns the orientation of the Robot in degree. 180° is opponent goal. Numbering goes clockwise
    def getKompass(self):
        kompass = (np.degrees(self.robot.pos[2]) + self.spielrichtung + 180) % 360
        return int(kompass + random.gauss(0, 1))

    # Sets the Motor speeds to this Value Motors rotate the Robot counter clockwise.
    # Numbering starts at the front and goes clockwise
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
        self.robot.motorSpeed(m0, m1, m2, m3)
        self.motor = np.array([m0,m1,m2,m3])

    # Toggles the kicker
    def Kick(self): #TODO Kick
        pass

    # Returns the State of the Robot
    # 1. In Game
    # 2. Defekt
    def getRobotState(self): #TODO getRobotState
        pass