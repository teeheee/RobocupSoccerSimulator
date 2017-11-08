import numpy as np
from robotRemote import RobotControl


#TODO make a realy good robot program

class Position:
    def __init__(self,x,y,px,py):
        self.x = x
        self.y = y
        self.px = px
        self.py = py

class SensorValues:
    def __init__(self,robot:RobotControl):
        self.robot = robot
        self.updateSensors()

    def updateSensors(self):
        self.ballsensors = self.robot.getIRBall()
        self.kompass = self.robot.getKompass()
        self.boden = self.robot.getBodenSensors()
        self.ultraschall = self.robot.getUltraschall()
        self.state = self.robot.getRobotState()

class RobotState:
    def __init__(self,sensors):
        self.sensors = sensors
        self.position = Position(0, 0, 0, 0)
        self.lastPosition = Position(0, 0, 0, 0)
        self.motorSpeed = [0,0,0,0]

    def drawEllipse(self, x, y, varx, vary):
        self.sensors.robot.drawEllipse(x, y, varx, vary)

    def updateState(self):
        self.sensors.updateSensors()
        stateUltraschall = self.updateUltraschall()

    def updateUltraschall(self):
        werte = self.sensors.ultraschall
        varx = abs(werte[0] + werte[2] - 160)
        vary = abs(werte[1] + werte[3] - 160)
        x = (werte[0] - werte[2]) / 2
        y = (werte[1] - werte[3]) / 2
        self.drawEllipse(x, y, varx, vary)
        return Position(x, y, varx, vary)

    def updateUltraschall(self):
        werte = self.sensors.ultraschall
        varx = abs(werte[0] + werte[2] - 160)
        vary = abs(werte[1] + werte[3] - 160)
        x = (werte[0] - werte[2]) / 2
        y = (werte[1] - werte[3]) / 2
        self.drawEllipse(x, y, varx, vary)
        return Position(x, y, varx, vary)


def main(robot:RobotControl):
    last_kompass = 0
    i_kompass = 0
    linieErkannt = False
    bodenrichtungLinie = -1
    lastMotorSpeed = [0,0,0,0]
    while True:

        # gather information
        ballsensors = robot.getIRBall()
        kompass = robot.getKompass()
        boden = robot.getBodenSensors()
        ultraschall = robot.getUltraschall()
        state = robot.getRobotState()

        #updateUltraschall(robot,ultraschall)

        if robot.getLightBarrier():
            robot.kick()

        # Linie
        bodenrichtung = -1  # finale fahrrtichtung für bodensensor
        for i in range(0, 16):
            if boden[i] > 0:
                if linieErkannt:
                    bodenrichtung = bodenrichtungLinie
                else:
                    bodenrichtungLinie = (i * 360 / 16 + 90) % 360
                    bodenrichtung = bodenrichtungLinie
                    linieErkannt = True
        if bodenrichtung == -1:
            linieErkannt = False



        # ballverfolgung
        ballrichtung = -1  # finale fahrrtichtung für ballsensor
        for i in range(0, 16):
            if ballsensors[i] > 0:
                ballrichtung = (i * 360 / 16 + 180 + 10) % 360
                if ultraschall[2] > 30:
                    if np.absolute(ballrichtung - 180) > 20:  # umfahren
                        if ballrichtung > 180:
                            ballrichtung = (ballrichtung + 90) % 360
                        else:
                            ballrichtung = (ballrichtung + 270) % 360

        # Statemachine
        if bodenrichtung > -1:  # linie
            fahrtrichtung = bodenrichtung
            geschwindigkeit = 100
        else:  # ball
            fahrtrichtung = ballrichtung
            geschwindigkeit = 100

        # calculate driving direction 180 is front

        p_faktor = 4
        d_faktor = 10
        i_faktor = 0# 0.1

        e_kompass = (180 - kompass)
        d_kompass = last_kompass - kompass
        if i_kompass > -1000 and i_kompass < 1000:
            i_kompass += e_kompass

        drall = p_faktor * e_kompass +  d_faktor * d_kompass + i_faktor * i_kompass



        fahrtrichtung = np.deg2rad(fahrtrichtung)

        m0 = -geschwindigkeit * np.cos(fahrtrichtung - 135) + drall
        m1 = -geschwindigkeit * np.cos(fahrtrichtung - 225) + drall
        m2 = -geschwindigkeit * np.cos(fahrtrichtung - 135) + drall
        m3 = -geschwindigkeit * np.cos(fahrtrichtung - 135) + drall

        robot.setMotorSpeed(m0,m1,m2,m3)

        lastMotorSpeed = [m0,m1,m2,m3]

        last_kompass = kompass