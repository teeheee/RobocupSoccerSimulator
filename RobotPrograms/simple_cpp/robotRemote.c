
/**** Thread handling part ***********/

#include "robotRemote.h"

struct ActuatorValueType actuatorValue;
struct SensorValueType sensorValue;
void (*threadWaiting)(void);
int accessFlag;

struct ActuatorValueType getActuatorValues()
{
    return actuatorValue;
}

void setSensorValues(struct SensorValueType aSensorValue)
{
    sensorValue = aSensorValue;
}

void setThreadWaitingCallback(void (*functionPtr)(void))
{
    threadWaiting = functionPtr;
}


/***** interface class implementation ****/


int* getBodenSensors()
{
    return sensorValue.line;
}

int* getUltraschall()
{
    return sensorValue.ultrasonic;
}

int* getIRBall()
{
    return sensorValue.ball;
}

int getKompass()
{
    return sensorValue.kompass;
}

int getLightBarrier()
{
    return sensorValue.lightBarrier;
}

void setMotorSpeed(int m0, int m1, int m2, int m3)
{
    actuatorValue.motors[0] = m0;
    actuatorValue.motors[1] = m1;
    actuatorValue.motors[2] = m2;
    actuatorValue.motors[3] = m3;
    threadWaiting();
}

void kick()
{
    actuatorValue.kick = 1;
}
