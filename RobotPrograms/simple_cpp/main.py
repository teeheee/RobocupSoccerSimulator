from robotRemote import RobotControl
from ctypes import *
import os

class SensorType(Structure):
    _fields_ = [
        ("line", c_int*16),
        ("ball", c_int*16),
        ("ultrasonic", c_int*4),
        ("kompass", c_int),
        ("lightBarrier", c_int),
        ("accelerometer", c_int*2),
        ("pixyBlocks", c_int*2), #TODO pixy struct!!!
        ("robotState", c_int)]

class ActuatorType(Structure):
    _fields_ = [
        ("motors", c_int*4),
        ("kick", c_int),
        ("dribbler", c_int)]
try:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    mainDLL = CDLL(dir_path+'/robot.so')
except:
    print("ERROR: C++ was not compiled correctly!!!")
    exit(1)

# This function is called every tick to update the SensorValues with the ones in RobotRemote Object
# It should be save because it is only called when the _main_ function is sleeping
def newOnUpdate(self): #TODO add sensor Values
    sensorValue = SensorType();
    for i in range(16):
        sensorValue.ball[i] = c_int(int(self.irsensors[i]))
    for i in range(16):
        sensorValue.line[i] = c_int(int(self.bodensensor[i]))
    sensorValue.kompass = c_int(self.kompass)
    sensorValue.lightBarrier = c_int(self.lightBarrier)
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
    robot.onUpdate = newOnUpdate
    mainDLL._main_()
