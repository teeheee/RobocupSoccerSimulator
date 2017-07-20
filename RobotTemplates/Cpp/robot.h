

int* getBodenSensors();
int* getUltraschall();
int* getPixy();
int* getIRBall();
int getKompass();
void setMotorSpeed(int m0, int m1, int m2, int m3);
void Kick();
int getRobotState();


void init();
void update(int* bodensensors, int* ultraschall, int* irball, int kompass, int robotstate);
int* getMotorspeed();