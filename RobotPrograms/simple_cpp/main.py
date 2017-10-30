from robotRemote import RobotControl
from ctypes import *

class SensorType(Structure):
    _fields_ = [
        ("infrared", c_int*16),
        ("line", c_int*16),
        ("ball", c_int),
        ("compass", c_int),
        ("lightbarrier", c_int)]


class ActuatorType(Structure):
    _fields_ = [
        ("motors", c_int*4),
        ("kick", c_int)]
try:
    mainDLL = CDLL('RobotPrograms/simple_cpp/robot.so') #TODO make this relative somehow!!!
except:
    print("ERROR: C++ was not compiled correctly!!!")
    exit(1)

# This function is called every tick to update the SensorValues with the ones in RobotRemote Object
# It should be save because it is only called when the _main_ function is sleeping
def newOnUpdate(self):
    sensorValue = SensorType();
    for i in range(16):
        sensorValue.infrared[i] = c_int(int(self.irsensors[i]))
    for i in range(16):
        sensorValue.line[i] = c_int(int(self.bodensensor[i]))
    sensorValue.compass = c_int(self.kompass)
    sensorValue.lightbarrier = c_int(self.lightBarrier)
    mainDLL.setSensorValues(sensorValue)
    actuatorValue = mainDLL.getActuatorValues()
    self.m0 = actuatorValue.motors[0]
    self.m1 = actuatorValue.motors[1]
    self.m2 = actuatorValue.motors[2]
    self.m3 = actuatorValue.motors[3]
    if actuatorValue.kick == 1:
        self.kickFlag = True


def main(robot:RobotControl):
    mainDLL.getActuatorValues.restype = ActuatorType

    def callback():
        robot.threadLock.acquire()
        robot.threadLock.wait()
        robot.threadLock.release()

    mainDLL.setThreadWaitingCallback(
        CFUNCTYPE(None)
        (callback)
    )

    robot.onUpdate = newOnUpdate
    mainDLL._main_()
