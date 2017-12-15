
#include "goldboard.h"

int motorspeeds[4];

Motor::Motor()
{
    for(int i = 0; i < 4; i++)
        motorspeeds[i]=0;
}

void Motor::rotate(int speed)
{
    motorspeeds[id]=speed;
    setMotorSpeed(motorspeeds[0],motorspeeds[1],motorspeeds[2],motorspeeds[3]);
}
void Motor::stop(bool bremsen) {}

CMPS03::CMPS03() {}
void CMPS03::init() {}
bool CMPS03::isInitialized() {
  return true;
}
int CMPS03::getValue()
{
    tick();
    return getKompass();
}
void CMPS03::setAs128Degree() {}

SRF08::SRF08()
{
}

void SRF08::init(int address) {}
void SRF08::changeAddress(int newAddress) {}

int SRF08::getValueCM()
{
    tick();
    int* tmp = getUltraschall();
    return tmp[id];
}

bool SRF08::isInitialized() { return true;}

Goldboard4::Goldboard4()
{
    for(int i = 0; i < 4; i++)
    {
        motor[i].id = sonar[i].id = i;
    }
}

/** Puts off all motors.
 */
void Goldboard4::setMotorsOff()
{
    setMotorSpeed(0,0,0,0);
    tick();
}

/** Sets a motor offset
 */
void Goldboard4::setMotorsOffset(int value){}

/** sets the given led id as led (NOTE: Then this pin cannot be used as button anymore)
 */
void Goldboard4::initLED(int i){}

/** Puts LED i on if state is true, else off
 */
void Goldboard4::setLed(int i, bool state){}

/** Puts the power output i on if state is true, else off
 */
void Goldboard4::setPower(int i, bool state){
    if(state == true)
        kick();
    tick();
}

/** Checks the state of button i. If it is pressed, true is returned,
 *  else false.
 */
bool getButton(int i){return false;}

/** Waits until button i is pressed and released again.
 */
void Goldboard4::waitForButton(int i){}

/** returns the value of the analog port i. 0 <= value <= 255
 */
int getAnalog(int i){return 0;}

/** returns true if the pwm port is logical high, else false.
 */
bool Goldboard4::getPWM(int i)
{
    return false;
}

/** returns true if the digital port is logical high, else false.
 */
bool Goldboard4::getDigital(int i) {
    return false;
}

/** returns the registered pulse length of the digital port i. 0 <= value <= 255
 */
int Goldboard4::getDigitalPulsedLight(int i)
{
    int* tmp = getIRBall();
    return tmp[i];
}

/** returns the registered pulse length of the pwm port i. 0 <= value <= 255
 */
int Goldboard4::getPWMPulsedLight(int i) {
    int* tmp = getIRBall();
    return tmp[i];
}