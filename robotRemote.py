import threading
import numpy as np


class robotThread (threading.Thread):
   def __init__(self, control, mainfunction):
        threading.Thread.__init__(self)
        self._control = control
        self._mainfunction = mainfunction
   def run(self):
        self._mainfunction(self._control)
        print("Error: robot %d finished his main loop. Check your code!" % self._control._robotInterface._id)

class RobotControl:
    def __init__(self, robotInterface, robotProgram):

        self._robotInterface = robotInterface

        # control attributes
        self.delayTimer = 0
        self.blocked = False
        self._motors = (0,0,0,0)
        self.kickFlag = 0
        self.timeinms = 0
        self.restartFlag = False
        self.state = self._robotInterface.getRobotState()
        self.US = self._robotInterface.getUltrasonic()
        self.pixy = self._robotInterface.getPixy()
        self.kompass = self._robotInterface.getKompass()
        self.irsensors = self._robotInterface.getIRBall()
        self.bodensensor = self._robotInterface.getLineSensors()
        self.lightBarrier = self._robotInterface.getLightBarrier()
        self.accelerometer = self._robotInterface.getAccelerometer()

        # in ms. has to be multiple of 10 because of update functino only checking every 10 ms.
        # this can be changed
        self.sensorTiming = {"compass" : 40,
                             "ultrasonic" : 100,
                             "pixy":   20,
                             "ir": 100,
                             "line": 10,
                             "lightBarrier": 10,
                             "accelerometer": 40}


        # threading attributes
        self.threadLock = threading.Condition()
        self.thread = robotThread(self, robotProgram.main)
        self.thread.daemon = True
        self.onUpdate = None # this is a function callback
        self.thread.start()


    # this function updates the sensorvalues for the main robot control thread in a pre defined frequency
    # dt is the tick time in ms

    def update(self, dt):

        self.timeinms += dt

        if self.delayTimer > 0:
            self.delayTimer -= 1
            return

        if self.timeinms % 10 == 0: #
            self.threadLock.acquire()
            self.state = self._robotInterface.getRobotState()
            if self.timeinms%self.sensorTiming["line"] == 0:
                self.bodensensor = self._robotInterface.getLineSensors()
            if self.timeinms%self.sensorTiming["compass"] == 0:
                self.kompass = self._robotInterface.getKompass()
            if self.timeinms%self.sensorTiming["ultrasonic"] == 0:
                self.US = self._robotInterface.getUltrasonic()
            if self.timeinms%self.sensorTiming["pixy"] == 0:
                self.pixy = self._robotInterface.getPixy()
            if self.timeinms%self.sensorTiming["ir"] == 0:
                self.irsensors = self._robotInterface.getIRBall()
            if self.timeinms%self.sensorTiming["lightBarrier"] == 0:
                self.lightBarrier = self._robotInterface.getLightBarrier()
            if self.timeinms%self.sensorTiming["accelerometer"] == 0:
                self.accelerometer = self._robotInterface.getAccelerometer()


            if self.onUpdate: #check if there is a function Callback registered for C++ interface
                self.onUpdate(self)

            if self.blocked == False:
                self._robotInterface.setMotorSpeed(self._motors[0],self._motors[1],self._motors[2],self._motors[3])
                if self.kickFlag == 1:
                    self._robotInterface.kick()
                    self.kickFlag = 0
                if self.restartFlag:
                    self._robotInterface.restartGame()
                    self.restartFlag = False
            self.threadLock.notify()
            self.threadLock.release()

    # plot(data) displays a plot of the given list of datapoints
    # the game is halted until the plot is closed.
    # be carefull with to many plot calls!
    def plot(self,data):
        self.threadLock.acquire()
        self._robotInterface.game.plot(data)
        self.threadLock.notify()
        self.threadLock.release()

    def drawEllipse(self,x,y,px,py):
        self.threadLock.acquire()
        self._robotInterface._game.debugOutput.drawEllipse(x,y,px,py)
        self.threadLock.notify()
        self.threadLock.release()

    def delay(self,ms):
        self.threadLock.acquire()
        self.delayTimer = ms
        self.threadLock.notify()
        self.threadLock.release()

    # Returns a list of 16 Analog Sensor Values representing Black and White and Green lines
    # Numbering starts at the front and goes clockwise
    def getBodenSensors(self):
        self.threadLock.acquire()
        tmp = np.array(self.bodensensor)
        self.threadLock.release()
        return tmp

    # Returns a list of 4 Distance measurements in all 4 directions
    # Numbering starts at the front and goes clockwise
    def getUltraschall(self):
        self.threadLock.acquire()
        tmp = np.array(self.US)
        self.threadLock.release()
        return tmp

    # Returns a List of Blocks of detected Objects
    # Attributes of each object is signature, x and y Position in camera vision
    # 1 is Ball
    # 2 is own Goal
    # 3 is opponent Goal
    # 4-9 are the Landmarks
    def getPixy(self):
        self.threadLock.acquire()
        tmp = np.array(self.pixy)
        self.threadLock.release()
        return tmp

    # Returns a list of 16 IR sensors. Value corresponds to distance from the Ball
    # Numbering starts at the front and goes clockwise
    def getIRBall(self):
        self.threadLock.acquire()
        tmp = np.array(self.irsensors)
        self.threadLock.release()
        return tmp

    # Returns the orientation of the Robot in degree. 180° is opponent goal. Numbering goes clockwise
    def getKompass(self):
        self.threadLock.acquire()
        tmp = np.array(self.kompass)
        self.threadLock.release()
        return tmp

    #Returns the current state of the light barrier
    def getLightBarrier(self):
        self.threadLock.acquire()
        tmp = self.lightBarrier
        self.threadLock.release()
        return tmp

    def getAccelerometer(self):
        self.threadLock.acquire()
        tmp = self.accelerometer
        self.threadLock.release()
        return tmp

    # Sets the Motor speeds to this Value Motors rotate the Robot counter clockwise.
    # Numbering starts at the front and goes clockwise
    def setMotorSpeed(self,m0,m1,m2,m3):
        self.threadLock.acquire()
        self._motors = (m0,m1,m2,m3)
        self.threadLock.wait()
        self.threadLock.release()

    # Toggles the kicker
    def kick(self):
        self.threadLock.acquire()
        self.kickFlag = 1
        self.threadLock.release()

    # Returns the State of the Robot
    # 0. enemy Goal
    # 1. Defekt
    # 2. In Game
    # 3. own Goal
    def getRobotState(self):
        self.threadLock.acquire()
        tmp = np.array(self.state)
        self.threadLock.release()
        return tmp


    def restartGame(self):
        self.threadLock.acquire()
        self.restartFlag = True
        self.threadLock.wait()
        self.threadLock.release()

    def block(self):
        self.blocked = True

    def unBlock(self):
        self.blocked = False





