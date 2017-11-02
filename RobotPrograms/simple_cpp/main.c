#include "robotRemote.h"
#include <stdio.h>

void _main_()
{
    while(1)
    {
        int p = getKompass();
        int k = (p-180)*0.1;
        printf("hllo %d\r\n",p);
        setMotorSpeed(k,k,k,k);
    }
}
