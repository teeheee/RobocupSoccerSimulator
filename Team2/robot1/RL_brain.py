

import numpy as np
import tensorflow as tf

np.random.seed(1)
tf.set_random_seed(1)


class DeepQNetwork:
    def __init__(self, input_count, output_count, batchsize, trainingdepth):
        self.action_memory = []
        self.observation_memory = []
        self.reward_memory = []
        self.action_episode = []
        self.reward_episode = []
        self.observation_episode = []
        self.input_count = int(input_count)
        self.output_count = int(output_count)
        self.hidden_count = int(output_count + (input_count - output_count)/2)
        self.batchsize = batchsize
        self.trainingdepth = trainingdepth
        self.erinnerung = 0.9
        self.episode_memory = []
        self.egreedy = 0.3

    def init_net(self):
    #    self.sensor_test_input = tf.placeholder(tf.float32, shape=[self.input_count], name = 'sensor-test-input')

     #   self.sensor_input = tf.placeholder(tf.float32, shape=[self.batchsize, self.input_count], name = 'sensor-input')
     #   self.action_input = tf.placeholder(tf.float32, shape=[self.batchsize, self.output_count], name = 'action-input')
     #   self.reward = tf.placeholder(tf.float32, shape=[self.batchsize], name = 'reward-input')

     #   self.weight1 = tf.Variable(tf.random_uniform([self.input_count,self.hidden_count],-1,1)  ,  name = 'weight1')
     #   self.weight2 = tf.Variable(tf.random_uniform([self.hidden_count,self.output_count],-1,1)  ,  name = 'weight2')

     #   self.bias1 = tf.Variable(tf.zeros([self.hidden_count])  ,  name = 'bias1')
     #   self.bias2 = tf.Variable(tf.zeros([self.output_count])  ,  name = 'bias2')

     #   layer1 = tf.sigmoid(tf.matmul(self.sensor_input,self.weight1) + self.bias1)
     #   self.q_values = tf.sigmoid(tf.matmul(layer1, self.weight2) + self.bias2)


     #   layer1_test = tf.sigmoid(tf.transpose(( self.sensor_test_input * tf.transpose(self.weight1) )) + self.bias1)
     #   self.q_values_test = tf.sigmoid(tf.matmul(layer1_test, self.weight2) + self.bias2)

    #    self.cost = tf.reduce_mean( tf.transpose((self.action_input - self.q_values) * (self.action_input - self.q_values)) * self.reward)

        self.sensor_input = tf.placeholder(tf.float32, shape=[self.input_count], name='sensor-test-input')

        self.weight1 = tf.Variable(tf.random_uniform([self.input_count,self.hidden_count],-1,1)  ,  name = 'weight1')
        self.weight2 = tf.Variable(tf.random_uniform([self.hidden_count,self.output_count],-1,1)  ,  name = 'weight2')

        #self.bias1 = tf.Variable(tf.zeros([self.hidden_count])  ,  name = 'bias1')
        #self.bias2 = tf.Variable(tf.zeros([self.output_count])  ,  name = 'bias2')

        layer1 = tf.sigmoid(tf.transpose(( self.sensor_input * tf.transpose(self.weight1) )))
        self.estimate_q_values = tf.matmul(layer1, self.weight2)
        self.real_q_values = tf.placeholder(shape=[1, self.output_count], dtype=tf.float32, name = 'next-q-value')

        self.cost = tf.reduce_sum( tf.square(self.estimate_q_values - self.real_q_values))

        self.training = tf.train.AdamOptimizer().minimize(self.cost)

        init = tf.global_variables_initializer()
        self.sess = tf.Session()
        self.sess.run(init)


    def learn_from_single_transistion(self, last_observation, estimated_reward, real_reward):
        self.sess.run(self.training, feed_dict={self.sensor_input: np.array(last_observation),
                                                self.estimate_q_values: np.array(estimated_reward),
                                                self.real_q_values: np.array(real_reward)})

    def store_transition(self, observation, action, reward):
        self.action_memory.append(action)
        self.observation_memory.append(observation)
        self.reward_memory.append(0)

        tmp = reward
        for lastReward in reversed(self.reward_memory):
            lastReward += tmp
            tmp = tmp * self.erinnerung

        if len(self.action_memory) > self.batchsize:
            self.reward_memory.pop()
            self.observation_memory.pop()
            self.action_memory.pop()

  #  def storeCurrentEpisode(self):
  #      pass# TODOOO!!!!!!!

    def choose_action(self, observation):
        if np.random.rand() < self.egreedy:
            return np.random.random_sample((self.input_count,))
        else:
            return self.sess.run(self.estimate_q_values, feed_dict={self.sensor_input:  np.array(observation)})

  #  def learn(self):
  #      if len(self.action_memory) == self.batchsize:
  #          for i in range(self.trainingdepth):
  #              self.sess.run(self.training, feed_dict = { self.sensor_input: np.array(self.observation_memory),
  #                                                         self.action_input: np.array(self.action_memory),
  #                                                         self.reward: np.array(self.reward_memory)})



