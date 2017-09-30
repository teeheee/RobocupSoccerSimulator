/***  TODO  Everything ****/


class RobotControl{
    Robot(int id);

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
}


extern 'C'{

    PyObject* getActuatorValues(int robotId);

    void updateSensorValues(PyObject* sensorValuesDictionary, int robotId);

    void startRobotMain();

}