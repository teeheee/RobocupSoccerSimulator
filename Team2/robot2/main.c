#include "robotRemote.h"

void _main_()
{
    while(1)
    {
        int* ir = getIRBall();
        int max_id = 0;
        for(int i = 0; i < 16; i++)
            if(ir[i] > 0)
                max_id = i;

        int richtung = max_id / 4;

        switch(richtung)
        {
            case 1:
                setMotorSpeed(100,-100,-100,100);
                break;
            case 0:
                setMotorSpeed(-100,-100,100,100);
                break;
            case 2:
                setMotorSpeed(-100,100,100,-100);
                break;
            case 3:
                setMotorSpeed(-100,-100,100,100);
                break;
            default:
                setMotorSpeed(0,0,0,0);
                break;
        }

    }
}