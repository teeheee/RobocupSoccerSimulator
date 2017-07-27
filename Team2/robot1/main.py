from robotRemote import RobotControl
from Team2.robot1.RL_brain import DeepQNetwork
import numpy as np
import matplotlib.pyplot as plt

last_irballsum = 0

def initEpisode():
    global last_irballsum
    last_irballsum = 0


def getReward(robot:RobotControl):

    state = robot.getRobotState()

    global last_irballsum
    irballsum = sum(robot.getIRBall())
    ballsensor = (irballsum-last_irballsum)/10
    last_irballsum = irballsum

    bodensensor = -sum(robot.getBodenSensors())/10

    reward = state + ballsensor + bodensensor

    return reward


def getObservation(robot:RobotControl):
    observation = []

    observation.extend(robot.getBodenSensors())

    irball = robot.getIRBall()
    observation.extend(irball/sum(irball))

    observation.extend([robot.getKompass()-180])

    us = robot.getUltraschall()
    observation.extend(us/sum(us))

    return np.array(observation)

def isEpisodeEnd(robot:RobotControl):
    if robot.getRobotState() != 0:
        return True
    return False

last_kompass = 0
i_kompass = 0
def doAction(robot:RobotControl , action):
    global i_kompass
    global last_kompass
    kompass = robot.getKompass()
    if action <= 8:
        geschwindigkeit=100
        fahrtrichtung = np.deg2rad(action*360/8)
        p_faktor = 1
        d_faktor = 4
        i_faktor = 0.05

        e_kompass = (180 - kompass)
        d_kompass = last_kompass - kompass
        if i_kompass > -1000 and i_kompass < 1000:
            i_kompass += e_kompass

        drall = p_faktor * e_kompass + d_faktor * d_kompass + i_faktor * i_kompass

        robot.setMotorSpeed(-geschwindigkeit * np.cos(fahrtrichtung - 135) + drall,
                            -geschwindigkeit * np.cos(fahrtrichtung - 225) + drall,
                            -geschwindigkeit * np.cos(fahrtrichtung - 315) + drall,
                            -geschwindigkeit * np.cos(fahrtrichtung - 45) + drall)

        last_kompass = kompass


def main(robot:RobotControl):
    RL = DeepQNetwork(16+16+4+1,8,2000,500)
    RL.init_net()
    step = 0
    rewardcounter = 0
    rewardmean = 0

    while True:

        observation = getObservation(robot)

        action = RL.choose_action(observation)

        a = np.argmax(action[0,:])
        doAction(robot,a)
        reward = getReward(robot)
        RL.learn_from_single_transistion(observation, action[0,:], reward)

        #if isEpisodeEnd(robot):
        #    RL.storeCurrentEpisode()
        #    RL.learn()

        step += 1