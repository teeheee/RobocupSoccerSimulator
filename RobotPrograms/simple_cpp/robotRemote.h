#ifndef _ROBOTREMOTE_H_
#define _ROBOTREMOTE_H_

#define MAX_PIXY_BLOCKS 10

typedef struct __attribute__((__packed__)){
    int signature;
    int x;
    int y;
    int x_size;
    int y_size;
} PixyBlockType;

typedef struct __attribute__((__packed__)){
    int size;
    PixyBlockType block[MAX_PIXY_BLOCKS];
} Blocks;


/*returns an Array with the values of 16 line sensors
* 1 means there is a white line (no black line)
* 0 means no line
*/
int* getBodenSensors();

/*returns an Array with the values of 4 Ultrasonic sensors
* 200 means no measurment possible cause the distance is to far or to short
* distance in mm
*/
int* getUltraschall();

/*returns all information like the real pixy
* BLOCKS blocks = pixyGetBlocks();
* blocks.size is the length of the block array
* blocks.block[i] is the block with id i (0 <= i < size)
* blocks.block[i].signature is the block signature
* blocks.block[i].x is the up down position on the camera vision
* blocks.block[i].y is the left right position on the camera vision
*/
Blocks pixyGetBlocks();

/*returns an Array with the values of the ir sensors
* Values decrease with distance to ball
*/
int* getIRBall();

/*returns the compass Value in degrees
* 180° is enemy goal
*/
int getKompass();

/*returns an 2D vektor with length = acceleration in the given direction*/
int* getAccelerometer();

/* returns 1 if the ball is in the ball capturing zone
* kick() is only possible when the ball is in the ball capturing zone
*/
int getLightBarrier();

//set the motor speed in percent for all 4 motors
void setMotorSpeed(int m0, int m1, int m2, int m3);

//activates the kicker of the robot
void kick();

//prints some text in the format of printf to the stdio
void print(const char * format, ... );

// returns the game state (like defekt, active, goal... )
int getRobotState();



/*** PRIVATE STUFF DON'T USE THIS ****/

typedef struct  __attribute__((__packed__)){
    int line[16];
    int ball[16];
    int ultrasonic[4];
    int kompass;
    int lightBarrier;
    int accelerometer[2];
    Blocks pixyBlocks;
    int robotState;
} SensorValueType;

typedef struct  __attribute__((__packed__)){
    int motors[4];
    int kick;
    int dribbler;
}ActuatorValueType ;

ActuatorValueType getActuatorValues();

void setSensorValues(SensorValueType sensorValuesDictionary);

void _main_();

#endif
