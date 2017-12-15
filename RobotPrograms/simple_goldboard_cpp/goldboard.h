#ifndef _GB_
#define _GB_

#include "robotRemote.h"

class Motor{
    public:
        Motor();
		void rotate(int speed);
		void stop(bool bremsen);
	    int id;
};

class CMPS03
{
	public:
		CMPS03();
		void init();
		bool isInitialized();
		int getValue();
		void setAs128Degree();
};


class SRF08
{
    public:
        SRF08(); // carefull the id has to be 0-4 not i2c adress!!!
        void			init(int address);
        void			changeAddress(int newAddress);
        int				getValueCM();
        bool			isInitialized();
	    int id;
};


class Goldboard4
{
    //variables
    public:
        Motor motor[4];
        CMPS03 compass;
        SRF08 sonar[4];

    //functions
    public:
        Goldboard4();

        /** Puts off all motors.
        */
        void setMotorsOff();

        /** Sets a motor offset
        */
        void setMotorsOffset(int value);

        /** sets the given led id as led (NOTE: Then this pin cannot be used as button anymore)
        */
        void initLED(int i);

        /** Puts LED i on if state is true, else off
        */
        void setLed(int i, bool state);

        /** Puts the power output i on if state is true, else off
        */
        void setPower(int i, bool state);

        /** Checks the state of button i. If it is pressed, true is returned,
        *  else false.
        */
        bool getButton(int i);

        /** Waits until button i is pressed and released again.
        */
        void waitForButton(int i);

        /** returns the value of the analog port i. 0 <= value <= 255
        */
        int getAnalog(int i);

        /** returns true if the pwm port is logical high, else false.
        */
        bool getPWM(int i);

        /** returns true if the digital port is logical high, else false.
        */
        bool getDigital(int i);

        /** returns pwm value
        */
        //int getPWM(int i);

        /** returns the registered pulse length of the digital port i. 0 <= value <= 255
        */
        int getDigitalPulsedLight(int i);

        /** returns the registered pulse length of the pwm port i. 0 <= value <= 255
        */
        int getPWMPulsedLight(int i);

}; //Goldboard4

#endif