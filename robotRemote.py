import threading
import numpy as np


class RobotControl:
    def __init__(self, robotInterface):
        self._robotInterface = robotInterface
        self.m0 = 0
        self.m1 = 0
        self.m2 = 0
        self.m3 = 0
        self.threadLock = threading.Condition()
        self._update()

    def _update(self):
        self.threadLock.acquire()
        self.bodensensor = self._robotInterface.getBodenSensors()
        self.US = self._robotInterface.getUltraschall()
        self.pixy = self._robotInterface.getPixy()
        self.kompass = self._robotInterface.getKompass()
        self.irsensors = self._robotInterface.getIRBall()
        self.state = self._robotInterface.getRobotState()
        self._robotInterface.setMotorSpeed(self.m0,self.m1,self.m2,self.m3)
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
    def getPixy(self): #TODO getPixy ist noch nicht fertig
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

    # Sets the Motor speeds to this Value Motors rotate the Robot counter clockwise.
    # Numbering starts at the front and goes clockwise
    def setMotorSpeed(self,m0,m1,m2,m3):
        self.threadLock.acquire()
        self.m0 = m0
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.threadLock.wait()
        self.threadLock.release()

    # Toggles the kicker
    def Kick(self): #TODO Kick
        pass

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



class robotThread (threading.Thread):
   def __init__(self, control, mainfunction):
        threading.Thread.__init__(self)
        self._control = control
        self._mainfunction = mainfunction
   def run(self):
        self._mainfunction(self._control)
        print("WTF!! robot %d finished his loop" % self._robotInterface.id)


def init(robotInterface):
    robotInterface.control = RobotControl(robotInterface)
    robotInterface.thread = robotThread(robotInterface.control,robotInterface.main)
    robotInterface.thread.daemon = True
    robotInterface.thread.start()


def tick(robotInterface):
    robotInterface.control._update()
