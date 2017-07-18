import numpy as np
# robot is from class interface

bounce = 0
lastdirection = 0

def tick(robot):
    #this is static
    global bounce
    global lastdirection

    geschwindigkeit = 50
    p_faktor = 0.5

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
            bodensensor1 = i * 360/16

    if bodensensor1 > -1:
        bodenrichtung = bodensensor1
        bounce = 2



    # ballverfolgung
    ballrichtung = -1 #finale fahrrtichtung für ballsensor
    for i in range(0,16):
        if ballsensors[i] > 0:
            ballrichtung = (i*360/16+180)%360
            if np.abs(ballrichtung-180) > 20: # umfahren
                if ballrichtung > 180:
                    ballrichtung = (ballrichtung + 90)% 360
                else:
                    ballrichtung = (ballrichtung + 270)%360


    # Statemachine
    if bounce > 0:
        bounce=bounce-1
        fahrtrichtung  = lastdirection
    elif bodenrichtung > -1:
        fahrtrichtung = (bodenrichtung+180)%360
        lastdirection = fahrtrichtung
    else:
        fahrtrichtung = (ballrichtung+180)%360


    # calculate driving direction 180 is front

    drall = p_faktor * (180-kompass)

    robot.setMotorSpeed(-geschwindigkeit*np.sin(fahrtrichtung-45)+drall,
                        -geschwindigkeit * np.sin(fahrtrichtung-135)+drall,
                        -geschwindigkeit * np.sin(fahrtrichtung-225)+drall,
                        -geschwindigkeit * np.sin(fahrtrichtung-315)+drall)


