import random
import numpy as np
import Team2.robot1.config as cfg

DATABASE = "replaymemory.npy"

class ReplayMemory:
    def __init__(self,maxsize):
        self.maxsize = maxsize
        self.Memory = {"Q_value": list(), "State": list() , "length": 0}
        self.TestMemory = {"Q_value": list(), "State": list() , "length": 0}
        self.Episode = {"State": [], "Q_value": [], "Reward": [], "Action": [], "length": 0}


    def addTransition(self,q_value,state,reward,action):
        self.Episode["State"].append(state)
        self.Episode["Q_value"].append(q_value)
        self.Episode["Action"].append(action)
        self.Episode["Reward"].append(reward)
        self.Episode["length"] += 1

    def _processEpisodeReward(self):
        tmp = 0
        for i in reversed(range(self.Episode["length"])):
            tmp = self.Episode["Reward"][i] + tmp * cfg.REGRED
            self.Episode["Reward"][i] = tmp

        self.rewardFromLastEpisode = self.Episode["Reward"]

        for i in range(self.Episode["length"]):
            action = np.array(self.Episode["Action"][i])
            #q_values = np.array(self.Episode["Q_value"][i])
            reward = np.array(self.Episode["Reward"][i])
            #update = 0.5 * q_values[action] + 0.5 * reward
            self.Episode["Q_value"][i][action] += reward

            q_value = self.Episode["Q_value"][i]

            self.Episode["Q_value"][i] = q_value / np.linalg.norm(q_value)


    def _getRandomSampels(self,percent):
        sampels = random.sample(range(self.Episode["length"]),int(self.Episode["length"]*percent))
        for i in sampels:
            self.Memory["Q_value"].append(self.Episode["Q_value"][i])
            self.Memory["State"].append(self.Episode["State"][i])
            if self.Memory["length"] > self.maxsize :
                sampel = np.random.randint(self.maxsize)
                del self.Memory["Q_value"][sampel]
                del self.Memory["State"][sampel]
            else:
                self.Memory["length"] += 1

        self.TestMemory = {"Q_value": list(), "State": list() , "length": 0}
        sampels = random.sample(range(self.Episode["length"]), int(self.Episode["length"]*percent))
        for i in sampels:
            self.TestMemory["Q_value"].append(self.Episode["Q_value"][i])
            self.TestMemory["State"].append(self.Episode["State"][i])

    def _clearEpisodeMemory(self):
        self.Episode = {"State": [], "Q_value": [], "Reward": [], "Action": [], "length": 0}


    def newEpisode(self):
        self._processEpisodeReward()
        self._getRandomSampels(cfg.MEMORY_SAMPLE_PERCENTAGE)
        self.rewardSum = sum(self.Episode["Reward"])
        self.memorySize = len(self.Memory["Q_value"])
        self._clearEpisodeMemory()

    def getTrainingData(self):
        return self.Memory

    def saveData(self):
        np.save(DATABASE,self.Memory)

    def loadData(self):
        try:
            self.Memory = np.load(DATABASE).item()
            return True
        except:
            return False