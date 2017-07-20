import threading
import Team2.robot1.main as m
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
        self._robotInterface.setMotorSpeed(self.m0,self.m1,self.m2,self.m3)
        self.threadLock.notify()
        self.threadLock.release()


class robotThread (threading.Thread):
   def __init__(self, control):
        threading.Thread.__init__(self)
        self._control = control
   def run(self):
        m.main(self._control)
        print("WTF!! robot %d finished his loop" % self._robotInterface.id)


def init(robotInterface):
    robotInterface.control = RobotControl(robotInterface)
    robotInterface.thread = robotThread(robotInterface.control)
    robotInterface.thread.daemon = True
    robotInterface.thread.start()


def tick(robotInterface):
    robotInterface.control._update()
