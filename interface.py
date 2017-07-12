import numpy as np
import threading
import socketserver
import subprocess


class threadedtcprequesthandler(socketserver.BaseRequestHandler): #TODO python interface
    def handle(self):
        print("robot joined")
        while (True):
            if self.server.off:
                dline = self.rfile.readline()
                print("server recv:" + dline)
                recvlist = [x.strip() for x in dline.split(',')]
                if len(recvlist) is not 5:
                    print("server: wrong package length")
                    break
                robotid = int(recvlist[0])
                if robotid < 1 or robotid > 4:
                    print("server: wrong robot id")
                    break
                robot = self.server.robots[robotid - 1]
                robot.motorspeed(float(recvlist[1]),
                                 float(recvlist[2]),
                                 float(recvlist[3]),
                                 float(recvlist[4]))
                ball = self.server.ball
                field = self.server.field
                points = field.getintersectingpoints(robot)
                bodensensor = np.zeros(16)
                for p in points:
                    bodensensor[int(np.degrees(np.arctan2(p[0], p[1])) * 16 / 360)] = 1
                response = str(robot.pos[0]) + "," + \
                           str(robot.pos[1]) + "," + \
                           str(robot.pos[2]) + "," + \
                           str(ball.pos[0]) + "," + \
                           str(ball.pos[1])
                for s in bodensensor:
                    response += "," + str(s)
                print("server send:" + response)
                self.wfile.write(response)
            else:
                break
        print("thread shutting down" + str(threading.current_thread()))


class threadedtcpserver(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def addstuff(self, _robots, _ball, _field):
        self.robots = _robots
        self.ball = _ball
        self.field = _field


class robot_interface_sockets:
    def __init__(self, robots, ball, field):
        # port 0 means to select an arbitrary unused port
        host, port = "localhost", 9996

        self.server = threadedtcpserver((host, port), threadedtcprequesthandler)
        ip, port = self.server.server_address
        self.server.addstuff(robots, ball, field)
        self.server.off = True

        # start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=self.server.serve_forever)
        # exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        self.processes = list()

    def startrobot(self, robotpath, _id):
        args = ["python", robotpath, str(_id)]
        self.processes.append(subprocess.Popen(args))

    def shutdown(self):
        for p in self.processes:
            p.terminate()
            p.wait()
        self.server.off = False
        self.server.server_close()
        print("server shutting down")
        self.server.shutdown()


### test interface... needs to be overcome :-d


class robot_interface:
    def __init__(self, _game, _robot, _spielrichtung):
        self.robot = _robot
        self.game = _game
        self.spielrichtung = _spielrichtung
        self.robot.motor = np.array([0, 0, 0, 0])
        self.bodensensor = np.zeros(16)
        self.timout = 0
        self.motor = np.array([0, 0, 0, 0])

    def getdata(self):
        self.richtung = (np.degrees(self.robot.pos[2]) + self.spielrichtung) % 360
        if self.spielrichtung == 180:
            self.position = np.array([-self.robot.pos[0], -self.robot.pos[1]])
        else:
            self.position = np.array([self.robot.pos[0], self.robot.pos[1]])

        self.bodensensor = np.zeros(16)

        points = self.game.field.getIntersectingPoints(self.robot)
        for p in points:
            self.bodensensor[int(np.degrees(np.arctan2(p[0], p[1])) * 16 / 360)] = 1

    def tick(self):
        self.getdata()

        points = self.game.field.getIntersectingPoints(self.robot)
        if len(points) > 0:
            richtung = (self.richtung + 180) % 360 - 180
            drall = -0.005 * richtung
            d = self.position
            distanz = np.linalg.norm(d)
            d = d / distanz
            self.robot.motorSpeed(-d[0] + drall, -d[1] + drall, d[0] + drall, d[1] + drall)
            return

        ball = self.game.ball

        if self.spielrichtung == 180:
            ballposition = (-ball.pos[0], -ball.pos[1])
        else:
            ballposition = ball.pos

        d = np.array(ballposition - self.position)
        distanz = np.linalg.norm(d)
        d = d / distanz
        richtung = (self.richtung + 180) % 360 - 180
        drall = -0.005 * richtung
        ballrichtung = np.degrees(np.arctan2(d[0], d[1]))
        if (ballrichtung > 80 and ballrichtung < 100) or distanz > 25:
            self.robot.motorSpeed(d[0] + drall, d[1] + drall, -d[0] + drall, -d[1] + drall)  # to the ball
        elif ballrichtung > 270 or ballrichtung < 80:
            self.robot.motorSpeed(-d[1] + drall, d[0] + drall, +d[1] + drall, -d[0] + drall)  # around the ball
        else:
            self.robot.motorSpeed(+d[1] + drall, -d[0] + drall, -d[1] + drall, +d[0] + drall)  # around the ball


class robot_defence_interface:
    def __init__(self, _game, _robot, _spielrichtung):
        self.robot = _robot
        self.game = _game
        self.spielrichtung = _spielrichtung
        self.robot.motor = np.array([0, 0, 0, 0])
        self.bodensensor = np.zeros(16)
        self.timout = 0
        self.motor = np.array([0, 0, 0, 0])

    def getdata(self):
        self.richtung = (np.degrees(self.robot.pos[2]) + self.spielrichtung) % 360
        if self.spielrichtung == 180:
            self.position = np.array([-self.robot.pos[0], -self.robot.pos[1]])
        else:
            self.position = np.array([self.robot.pos[0], self.robot.pos[1]])

        self.bodensensor = np.zeros(16)

        points = self.game.field.getintersectingpoints(self.robot)
        for p in points:
            self.bodensensor[int(np.degrees(np.arctan2(p[0], p[1])) * 16 / 360)] = 1

    def tick(self):
        self.getdata()

        points = self.game.field.getintersectingpoints(self.robot)
        if len(points) > 0:
            # print("linie!")
            richtung = (self.richtung + 180) % 360 - 180
            drall = -0.005 * richtung
            d = self.position
            distanz = np.linalg.norm(d)
            # print("distanz = ",distanz)
            d = d / distanz
            # print("d = ",d)
            self.robot.motorspeed(-d[0] + drall, -d[1] + drall, d[0] + drall, d[1] + drall)
            return
        mgf = (((self.richtung) % 360)) * -0.0005
        # drall = -0.005*richtung
        ball = self.game.ball
        #                if len(points) > 0:
        #                    d = self.position
        #                    self.robot.motorspeed(-d[0]+drall,-d[1]+drall,d[0]+drall,d[1]+drall)
        #                    return

        # else:

        if self.spielrichtung == 180:
            ballpos = (-ball.pos[0] - self.position[0], -ball.pos[1] - self.position[1])
        else:
            ballpos = (ball.pos[0] - self.position[0], ball.pos[1] - self.position[1])
        # ballposition[0] > 0 ball vorne
        # ballposition[0] < 0 ball hinten
        # ballposition[1] > 0 ball rechts
        # ballposition[1] < 0 ball links

        # ballrichtung = np.degrees(np.arctan2(ballposition[0],ballposition[1])) # ball vorne bei ballrichtung = 180
        # ballposition = ball_richtung(ballpos[0],ballpos[1],self.richtung)
        ballposition = ball_richtung(ballpos[0], ballpos[1], 0)
        if (self.position[0] > -80):
            ball = driveball(0, int(ballposition), False)
        else:
            ball = driveball(0, int(ballposition), True)
        # print("ballposition = ",ballpos)
        # print("self.position = ",self.position//1)
        # print("richtung = ",mgf)
        # print("driveball = ",ball)
        speed = 4
        if (0 == 1):
            pass
        # ball sehr nahe
        if (abs(ballpos[0]) < 20 and abs(ballpos[1]) < 20):
            # print("naher ball")
            sp = drive((ball - self.richtung), speed, mgf)
        # hinten bleiben
        elif (self.position[0] > -50):
            # print("vorne von tor weg!")
            # sp = drive(180,speed*-(self.position[0]-50)+20,mgf)
            sp = drive((180 - self.richtung), speed * 2, mgf)
        # self.robot.motorspeed(-speed*-(self.position[0]-50),0,+speed*-(self.position[0]-50),0)      # drive backward
        # links bleiben
        elif (self.position[1] < -35):
            # print("links von tor weg")
            sp = drive((90 - self.richtung), speed * 2, mgf)
        # self.robot.motorspeed(0,-speed*(self.position[0]-35),0,+speed*(self.position[0]-35))      # drive backward
        # rechts bleiben
        elif (self.position[1] > 35):
            # print("rechts von tor weg")
            sp = drive((270 - self.richtung), speed * 2, mgf)
        # self.robot.motorspeed(0,+speed*(self.position[0]+35),0,-speed*(self.position[0]+35))      # drive backward
        # ball vorne, roboter aber schon weit vorn
        elif ((self.position[0] > -60) and (ball == 0)):
            # print("ball vorne, aber weit weg")
            sp = 0, 0, 0, 0
        else:
            # print("else")
            # if (ball >= 0) and (ball < 360):
            # sp = drive(ball,speed*200,mgf)
            sp = drive((ball - self.richtung), speed, mgf)
        # else:
        # sp = 0,0,0,0
        # print(sp)
        self.robot.motorspeed(sp[0], sp[1], sp[2], sp[3])
        # self.robot.motorspeed(0,0,0,0)
