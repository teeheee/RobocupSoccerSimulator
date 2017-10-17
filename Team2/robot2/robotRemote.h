#ifndef _ROBOTREMOTE_H_
#define _ROBOTREMOTE_H_


int* getBodenSensors();
int* getUltraschall();
//Blocks* getPixy();
int* getIRBall();
int getKompass();
int getLightBarrier();

void setMotorSpeed(int m0, int m1, int m2, int m3);
void kick();

void plot(int* data, int datasize);
//State getRobotState();
void restartGame();



/*** PRIVATE STUFF DON'T USE THIS ****/

struct SensorValueType{
    int line[16];
    int ball[16];
    int ultrasonic[4];
    int kompass;
    int lightBarrier;
};

struct ActuatorValueType{
    int motors[4];
    int kick;
};

void setThreadWaitingCallback(void (*functionPtr)(void));

struct ActuatorValueType getActuatorValues();

void setSensorValues(struct SensorValueType sensorValuesDictionary);

void _main_();

#endif