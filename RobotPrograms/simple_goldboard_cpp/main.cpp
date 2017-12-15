#include "goldboard.h"
#include <math.h>

Goldboard4 gb;

void _main()
{
    while(1)
    {
        int x=0,y=0;
        int irValues[16];
        for(int index = 0; index < 16; index ++)
            irValues[index] = gb.getPWMPulsedLight(index);

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

        int drall = -(gb.compass.getValue()-180);

        gb.motor[0].rotate((-x+y)+drall);
        gb.motor[1].rotate((-x-y)+drall);
        gb.motor[2].rotate((x-y)+drall);
        gb.motor[3].rotate((x+y)+drall);
    }
}
