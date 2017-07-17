import numpy as np
# robot is from class interface


def tick(robot):

    # gather information
    ballsensors = robot.getIRBall()
    kompass = robot.getKompass()
    boden = robot.getBodenSensors()
    ultraschall = robot.getUltraschall()

    bodenrichtung = -1
    for i in range(0,16):
        if boden[i] > 0:
            bodenrichtung = i*360/16



    ballrichtung = -1
    for i in range(0,16):
        if ballsensors[i] > 0:
            ballrichtung = i*360/16

    if np.abs(ballrichtung-180) > 10:
        if ballrichtung > 180:
            ballrichtung = ballrichtung - 90
        else:
            ballrichtung = ballrichtung + 90


    if bodenrichtung > -1:
        fahrtrichtung = 360-bodenrichtung
    else:
        fahrtrichtung = ballrichtung

    # calculate driving direction
    geschwindigkeit = 50

    p_faktor = 1
    drall = p_faktor * (180-kompass)

    robot.setMotorSpeed(-geschwindigkeit*np.sin(fahrtrichtung-45)+drall,
                        -geschwindigkeit * np.sin(fahrtrichtung-135)+drall,
                        -geschwindigkeit * np.sin(fahrtrichtung-225)+drall,
                        -geschwindigkeit * np.sin(fahrtrichtung-315)+drall)
