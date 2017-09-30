/***** interface class implementation ****/

/***  TODO  Everything ****/


/**** Thread handling part ***********/

#include <pthread.h>

struct SensorValues{
    int line[16];
    int ball[16];
    int ultrasonic[4];
};

struct ActuatorValues{
    int motors[4];
};

struct Robot{
    SensorValues sensors;
    ActuatorValues actuators;
};

Robot robots[4];

PyObject* getActuatorValues(int robotId)
{

}

void updateSensorValues(PyObject* sensorValuesDictionary, int robotId)
{

}

void startRobotMain()
{

}