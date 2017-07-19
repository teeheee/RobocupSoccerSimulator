import numpy as np
# robot is from class interface

# Torwart
letzterichtung = -1

def tick(robot):
    #this is static
    global letzterichtung


    # gather information
    ballsensors = robot.getIRBall()
    kompass = robot.getKompass()
    boden = robot.getBodenSensors()
    ultraschall = robot.getUltraschall()


    # Linie
    bodenrichtung = -1 #finale fahrrtichtung für bodensensor
    bodensensor1 = -1
    for i in range(0,16):
        if boden[i] > 0:
            bodensensor1 = i

    if letzterichtung > -1:
        bodenrichtung = letzterichtung
    if bodensensor1 > -1:
        bodenrichtung = (bodensensor1 * 360/16)%360
        bodenrichtung = letzterichtung = bodenrichtung
    else:
        letzterichtung = -1



    # ballverfolgung
    ballrichtung = -1 #finale fahrrtichtung für ballsensor
    for i in range(0,16):
        if ballsensors[i] > 0:
            ballrichtung = (i*360/16+180 + 10) % 360

    usrichtung = -1
    if ultraschall[2]>30:
        usrichtung = 0


    # Statemachine
    if bodenrichtung > -1: #linie
        fahrtrichtung = bodenrichtung
        geschwindigkeit = 100
    elif usrichtung > -1:
        fahrtrichtung = usrichtung
        geschwindigkeit = 100
    else: #ball
        fahrtrichtung = ballrichtung
        geschwindigkeit = 100


    # calculate driving direction 180 is front
    p_faktor = 1
    drall = p_faktor * (180-kompass)
    fahrtrichtung = np.deg2rad(fahrtrichtung)
    robot.setMotorSpeed(-geschwindigkeit*np.cos(fahrtrichtung-135)+drall,
                        -geschwindigkeit * np.cos(fahrtrichtung-225)+drall,
                        -geschwindigkeit * np.cos(fahrtrichtung-315)+drall,
                        -geschwindigkeit * np.cos(fahrtrichtung-45)+drall)


