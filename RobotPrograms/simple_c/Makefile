FLAGS = -shared -fPIC -Wall -lm

all: robot.so

robot.so: robotRemote.c main.c
	 gcc $(FLAGS) -o robot.so robotRemote.c main.c robotRemote.h
     
cleanall:
	 rm robot.so
