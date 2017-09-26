import numpy as np
import tensorflow as tf
import Team2.robot1.NeuralNetwork as nn
import Team2.robot1.ReplayMemory as rm
import Team2.robot1.config as cfg

np.random.seed(1)
tf.set_random_seed(1)


class DeepQNetwork:
    def __init__(self, input_count, output_count, memorySize):
        self.input_count = input_count
        self.output_count = output_count
        self.replayMemory = rm.ReplayMemory(memorySize)
        self.neuralNetwork = nn.NeuralNetwork(input_count,output_count)
        self.epislon_greedy = 1

    def isPopulated(self):
        if self.replayMemory.loadData():
            self.neuralNetwork.trainingdepth = 1000
            self.learn()
            self.neuralNetwork.trainingdepth = cfg.LEARNING_DEPTH
            return True
        else:
            return False

    def store_transition(self, observation, action, reward, q_value):
        self.replayMemory.addTransition(q_value,observation,reward,action)

    def storeCurrentEpisode(self):
        self.replayMemory.newEpisode()


    def choose_action(self, observation):
        if  np.random.random_sample() < self.epislon_greedy:
            return np.random.random_sample(self.output_count, )
        else:
            action = self.neuralNetwork.forwardPass(observation)
            return action[0]

    def learn(self):
        #print("training started.... ")
        Data = self.replayMemory.getTrainingData()
        self.neuralNetwork.train(Data["State"],Data["Q_value"])
        self.epislon_greedy = self.epislon_greedy*cfg.GREEDY
        #print("training finished")

    def test(self):
        n = 0
        i = 0
        for state in self.replayMemory.TestMemory["State"]:
            q_value = self.neuralNetwork.forwardPass(state)
            n += np.linalg.norm(q_value-self.replayMemory.TestMemory["Q_value"][i])
            i += 1
        if i == 0:
            return n
        return n/i



