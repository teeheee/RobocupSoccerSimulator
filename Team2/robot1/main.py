from robotRemote import RobotControl
from Team2.robot1.RL_brain import DeepQNetwork
import Team2.robot1.config as cfg
import numpy as np


last_irballsum = 0

def initEpisode():
    global last_irballsum
    last_irballsum = 0


def getReward(robot:RobotControl):

    state = robot.getRobotState()*5

    #check if Ball gets closer
    global last_irballsum
    irballsum = sum(robot.getIRBall())
    ballsensor = (irballsum-last_irballsum)/12
    last_irballsum = irballsum

    #check if line sensor are activated
    bodensensor = -sum(robot.getBodenSensors())/6

    #sum the reward
    reward = state + ballsensor #+ bodensensor

    return reward


def getObservation(robot:RobotControl):
    observation = []

    observation.extend(robot.getBodenSensors())

    irball = robot.getIRBall()
    if sum(irball) == 0:
        observation.extend(irball)
    else:
        observation.extend(irball/sum(irball))

    #observation.extend([robot.getKompass()-180])

    us = robot.getUltraschall()
    observation.extend(us/200)

    return np.array(observation)

def isEpisodeEnd(robot:RobotControl):
    if robot.getRobotState() != 0:
        return True
    return False

last_kompass = 0
i_kompass = 0
def doAction(robot:RobotControl , action):
    for i in range(10):
        if isEpisodeEnd(robot):
            return
        global i_kompass
        global last_kompass
        kompass = robot.getKompass()
        if action <= 8:
            geschwindigkeit=100
            fahrtrichtung = np.deg2rad(action*360/4)
            p_faktor = 6
            d_faktor = 20

            e_kompass = (180 - kompass)
            d_kompass = last_kompass - kompass

            drall = p_faktor * e_kompass + d_faktor * d_kompass

            robot.setMotorSpeed(-geschwindigkeit * np.cos(fahrtrichtung - 135) + drall,
                                -geschwindigkeit * np.cos(fahrtrichtung - 225) + drall,
                                -geschwindigkeit * np.cos(fahrtrichtung - 315) + drall,
                                -geschwindigkeit * np.cos(fahrtrichtung - 45) + drall)

            last_kompass = kompass


def main(robot:RobotControl):
    RL = DeepQNetwork(16+16+4,4,cfg.MEMORY_SIZE)
    episodeCounter = 0
    tickCounter = 0
    LOG = {"timeout": 0,
           "win": 0,
           "lose": 0,
           "outofbounce": 0}

    if RL.isPopulated():
        print("Loading database")
        episodeCounter = cfg.POPULATING_EPISODES

    while True:
        tickCounter+=1

        observation = getObservation(robot)
        action = RL.choose_action(observation)
        action_id = np.argmax(action)
        doAction(robot,action_id)
        reward = getReward(robot)
        if tickCounter > 100: # timeout
            reward-=1
        RL.store_transition(observation, action_id, reward, action)



        if isEpisodeEnd(robot) or tickCounter>100: # New episode
            robot.setMotorSpeed(0,0,0,0)
            tickCounter = 0
            episodeCounter += 1
            print("-------episode: " + str(episodeCounter) + "--------")

            if episodeCounter < cfg.POPULATING_EPISODES:                 # populating Database
                RL.storeCurrentEpisode()
                print("POPULATING")
                print("memory Size: " + str(RL.replayMemory.memorySize))
                for i in range(50): # some delay
                    robot.setMotorSpeed(0, 0, 0, 0)

            elif episodeCounter < cfg.POPULATING_EPISODES+cfg.LEARNING_EPISODES:              # learning
                RL.storeCurrentEpisode()
                if episodeCounter%(cfg.LEARNING_DELAY*RL.replayMemory.memorySize/1000) == 0:
                    RL.learn()
                    convergenz = RL.test()
                    RL.replayMemory.saveData()
                    print("TRAINING")
                    print("memory Size: " + str(RL.replayMemory.memorySize))
                    print("reward: " + str(RL.replayMemory.rewardSum))
                    print("epsilon_greedy: " + str(RL.epislon_greedy))
                    print("convergenz: " + str(convergenz))
            elif episodeCounter < cfg.POPULATING_EPISODES+cfg.LEARNING_EPISODES+cfg.TESTING_EPISODES:              # testing
                print("TESTING")
                if robot.getRobotState() == 0:
                    LOG["timeout"]+=1
                if robot.getRobotState() == 5:
                    LOG["win"]+=1
                if robot.getRobotState() == -5:
                    LOG["lose"]+=1
                if robot.getRobotState() == -2:
                    LOG["outofbounce"]+=1
            else: # finished
                print("FINISHED")
                print("win: "+ str(LOG["win"]))
                print("lose: "+ str(LOG["lose"]))
                print("outofbounce: "+ str(LOG["outofbounce"]))
                print("timeout: "+ str(LOG["timeout"]))
                RL.replayMemory.saveData()
                robot.plot([0,0,0,0,0])
            robot.restartGame()
            initEpisode()


