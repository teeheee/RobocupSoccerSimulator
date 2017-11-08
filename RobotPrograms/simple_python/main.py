from robotRemote import RobotControl
import numpy as np


def cosDeg(degree):
    return np.cos(np.deg2rad(degree))

def main(robot:RobotControl):
    last_kompass = 0
    i_kompass = 0

    while True:

        # gather information
        ballsensors = robot.getIRBall()
        kompass = robot.getKompass()
        boden = robot.getBodenSensors()
        ultraschall = robot.getUltraschall()

        if robot.getLightBarrier():
            robot.kick()

        # Linie
        bodenrichtung = -1  # finale fahrrtichtung für bodensensor
        for i in range(0, 16):
            if boden[i] > 0:
                bodenrichtung = (i * 360 / 16) % 360



        # ballverfolgung
        ballrichtung = -1  # finale fahrrtichtung für ballsensor
        for i in range(0, 16):
            if ballsensors[i] > 0:
                ballrichtung = (i * 360 / 16 + 180) % 360
                if ultraschall[2] > 30:
                    if np.absolute(ballrichtung - 180) > 30 and ballsensors[i] > 50:  # umfahren
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

        p_faktor = 1
        d_faktor = 3
        i_faktor = 0.01

        e_kompass = (180 - kompass)
        d_kompass = last_kompass - kompass
        if i_kompass > -1000 and i_kompass < 1000:
            i_kompass += e_kompass

        drall = p_faktor * e_kompass +  d_faktor * d_kompass + i_faktor * i_kompass



        robot.setMotorSpeed(-geschwindigkeit * cosDeg(fahrtrichtung - 135) + drall,
                            -geschwindigkeit * cosDeg(fahrtrichtung - 225) + drall,
                            -geschwindigkeit * cosDeg(fahrtrichtung - 315) + drall,
                            -geschwindigkeit * cosDeg(fahrtrichtung - 45) + drall)



        last_kompass = kompass