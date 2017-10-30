FLAGS = -shared -fPIC

all: robot.so

robot.so: robotRemote.c main.c
	 gcc $(FLAGS) -o robot.so robotRemote.c main.c robotRemote.h
     
clean:
	 rm robot.so
