import tensorflow as tf
import numpy as np
import Team2.robot1.config as cfg

class NeuralNetwork:
   def __init__(self,input_count, output_count):
       self.input_count = input_count
       self.output_count = output_count
       self.hidden_count = int(output_count + (input_count - output_count)/2)
       self.learning_rate = cfg.LEARNING_RATE
       self.trainingdepth = cfg.LEARNING_DEPTH

       self.sensor_input = tf.placeholder(tf.float32, shape=[None, self.input_count], name='sensor-input')
       self.q_value = tf.placeholder(tf.float32, shape=[None, self.output_count], name='q_value')

       self.weight1 = tf.Variable(tf.random_uniform([self.input_count, self.hidden_count], -1, 1), name='weight1')
       self.weight2 = tf.Variable(tf.random_uniform([self.hidden_count, self.output_count], -1, 1), name='weight2')

       self.bias1 = tf.Variable(tf.zeros([self.hidden_count]), name='bias1')
       self.bias2 = tf.Variable(tf.zeros([self.output_count]), name='bias2')


       layer1 = tf.sigmoid(tf.matmul(self.sensor_input, self.weight1) + self.bias1)
       self.hypothesis = tf.tanh(tf.matmul(layer1, self.weight2) + self.bias2)


       # Define loss and optimizer
       loss_op = tf.reduce_sum((self.hypothesis - self.q_value) * (self.hypothesis - self.q_value))
       optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
       self.training = optimizer.minimize(loss_op)

       init = tf.global_variables_initializer()
       self.sess = tf.Session()
       self.sess.run(init)


   def train(self,inputData,outputData):
       if len(inputData) != len(outputData):
           print("error with training data")
       for i in range(self.trainingdepth):
           self.sess.run(self.training, feed_dict={self.sensor_input: np.array(inputData),
                                                   self.q_value: np.array(outputData)})
   def forwardPass(self,input):
       return self.sess.run(self.hypothesis, feed_dict={self.sensor_input: np.array([input])})