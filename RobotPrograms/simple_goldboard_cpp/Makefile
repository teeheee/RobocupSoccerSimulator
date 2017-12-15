
FLAGS = -std=gnu++11  -shared -fPIC -Wall -lm -fno-strict-aliasing -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security  -DNDEBUG -g -fwrapv -O2 -Wall


all: robot.so

robot.so: main.cpp robotRemote.cpp goldboard.cpp
	 g++ $(FLAGS) -o robot.so robotRemote.cpp main.cpp robotRemote.h goldboard.h goldboard.cpp

cleanall:
	 rm robot.so
