import time
from gameconfig import gc

# This class is just for debugging Cpu Time usage

class CpuTime:
    def __init__(self):
        self.lastTime = time.clock()

    def restartTimer(self):
        self.lastTime = time.clock()

    def printTimer(self, aName):
        if gc.GUI["ShowTiming"]:
            timePassed = self.lastTime - time.clock()
            print(aName + ": "+ str(int(timePassed*1000000)))
            self.restartTimer()


cputime = CpuTime()