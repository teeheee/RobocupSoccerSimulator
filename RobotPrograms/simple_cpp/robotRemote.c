
/**** Thread handling part ***********/

#include "robotRemote.h"
#include <stdio.h>
#include <stdarg.h>

ActuatorValueType actuatorValue;
SensorValueType sensorValue;
int accessFlag;

ActuatorValueType getActuatorValues()
{
    accessFlag = 0;
    return actuatorValue;
}

void setSensorValues(SensorValueType aSensorValue)
{
    sensorValue = aSensorValue;
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

int* getAccelerometer()
{
    return sensorValue.accelerometer;
}

int getKompass()
{
    return sensorValue.kompass;
}

int getLightBarrier()
{
    return sensorValue.lightBarrier;
}

Blocks pixyGetBlocks()
{
    return sensorValue.pixyBlocks;
}


int getRobotState()
{
    return sensorValue.robotState;
}


void setMotorSpeed(int m0, int m1, int m2, int m3)
{
    actuatorValue.motors[0] = m0;
    actuatorValue.motors[1] = m1;
    actuatorValue.motors[2] = m2;
    actuatorValue.motors[3] = m3;
    accessFlag=1;
    while(accessFlag);
}

void kick()
{
    actuatorValue.kick = 1;
}


void print(const char * format, ... )
{
    va_list args;
    va_start(args, format);
    printf(format, args);
    va_end(args);
}


