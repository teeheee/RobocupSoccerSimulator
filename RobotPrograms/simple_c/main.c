#include "robotRemote.h"
#include <math.h>

void _main_()
{
    while(1)
    {
        int x=0,y=0;

        int* irValues = getIRBall();
        int sum = 0;
        int maxIndex = 0;
        for(int index = 0; index < 16; index ++)
        {
            sum += irValues[index];
            if(irValues[maxIndex] < irValues[index])
                maxIndex = index;
        }

        float winkel = (3.1415*2.0/16.0)*maxIndex;
        x = 100*cos(winkel);
        y = 100*sin(winkel);

        int drall = -(getKompass()-180);
        setMotorSpeed((-x+y)+drall,(-x-y)+drall,(x-y)+drall,(x+y)+drall);
    }
}
