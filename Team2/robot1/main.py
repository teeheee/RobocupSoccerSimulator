from robotRemote import RobotControl
from Team2.robot1.RL_brain import DeepQNetwork
import numpy as np

last_irballsum = 0
def getReward(robot:RobotControl):
    state = robot.getRobotState()*10
    global last_irballsum
    irballsum = sum(robot.getIRBall())
    ballsensor = (irballsum-last_irballsum)
    last_irballsum = irballsum

    #bodensensor = sum(robot.getBodenSensors())*10

    reward = state
    if reward == 0:
        reward = ballsensor
    else:
        last_irballsum = 15
    return reward


def getObservation(robot:RobotControl):
    observation = []
    observation.extend(robot.getBodenSensors())
    observation.extend(robot.getIRBall())
    observation.extend([robot.getKompass()])
    observation.extend(robot.getUltraschall())
    return np.array(observation)


last_kompass = 0
i_kompass = 0
def doAction(robot:RobotControl , action):
    global i_kompass
    global last_kompass
    kompass = robot.getKompass()
    if action <= 16:
        geschwindigkeit=100
        fahrtrichtung = np.deg2rad(action*360/8)
        p_faktor = 3
        d_faktor = 12
        i_faktor = 0.001

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
    RL = DeepQNetwork(n_actions=8,
                      n_features=16+4+16+1,
                      learning_rate=0.005,
                      reward_decay=0.99,
                      e_greedy=0.8,
                      replace_target_iter=1000,
                      memory_size=10000,
                      output_graph=True
                      )
    observation = getObservation(robot)
    step = 0
    rewardcounter = 0
    rewardmean = 0
    while True:

        action = RL.choose_action(observation)

        doAction(robot,action)

        observation2 = getObservation(robot)

        reward = getReward(robot)

        RL.store_transition(observation, action, reward, observation2)
        rewardcounter+=reward

        if (step % 20 == 0):
            RL.learn()

        if (step % 500 == 0):
            rewardmean = rewardmean*0.8 + rewardcounter*0.2
            print("overall reward: %d at generation %d" % (rewardmean, step/20))
            rewardcounter = 0

        step += 1