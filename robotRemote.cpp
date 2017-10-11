
/**** Thread handling part ***********/
#include <Python.h>

struct SensorValues{
    int line[16];
    int ball[16];
    int ultrasonic[4];
    int kompass;
    int lightBarrier;
};

struct ActuatorValues{
    int motors[4];
    int kick;

};

struct Robot{
    SensorValues sensors;
    ActuatorValues actuators;
};

Robot robots[4];

PyObject* getActuatorValues(int robotId)
{
    PyObject* ret = PyDict_New()
    PyObject* motors = PyList_New()
    for( int i = 0; i < 4; i++)
        PyList_Append(motors,PyInt_FromLong(robots[robotId].actuators.motors[i]))
    PyDict_SetItemString(ret,"Motors",motors)
}

void setSensorValues(PyObject* sensorValuesDictionary, int robotId)
{

}

void startRobotMain()
{

}


/***** interface class implementation ****/


RobotControl::RobotControl(int id)
{
    _id = id
}

int* RobotControl::getBodenSensors()
{
    return robots[_id].sensors.line;
}

int* RobotControl::getUltraschall()
{
    return robots[_id].sensors.ultrasonic;
}
//Blocks* RobotControl::getPixy()
int* RobotControl::getIRBall()
{
    return robots[_id].sensors.ball;
}

int RobotControl::getKompass()
{
    return robots[_id].sensors.kompass;
}

int RobotControl::getLightBarrier()
{
    return robots[_id].sensors.lightBarrier;
}

void RobotControl::setMotorSpeed(int m0, int m1, int m2, int m3)
{
    robots[_id].actuators.motors[0] = m0;
    robots[_id].actuators.motors[1] = m1;
    robots[_id].actuators.motors[2] = m2;
    robots[_id].actuators.motors[3] = m3;
}

void RobotControl::kick()
{
    robots[_id].actuators.kick = 1;
}

/*void RobotControl::plot(int* data, int datasize)
{

}

State getRobotState();

void RobotControl::restartGame()
{

}

*/