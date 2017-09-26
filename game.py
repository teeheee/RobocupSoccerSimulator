import Team1.robot1.main as r1
import Team1.robot2.main as r2
import Team2.robot1.main as r3
import Team2.robot2.main as r4
import robotRemote
from grafik import *
from physik import *
import matplotlib.pyplot as plt
from gameconfig import gc
import time

class Robot:
    # display ist das pygame fenster
    # space ist der pymunk Raum
    # _id is die Roboter ID
    # color ist die Farbe des Roboters
    def __init__(self, display, space, _id, color ,direction):
        self.direction = direction
        self.grafik = RobotGrafik(display, _id, color, direction)  # Physik
        self.physik = RobotPhysik(space, self.grafik)
        self.orientation = direction
        # Roboter ID (setzt fest, welche Nummer auf dem Roboter steht)
        self.id = _id
        # Roboter Position in (x, y, rotation) Mittelpunkt ist x=0 y=0
        self.pos = np.array([0, 0, 0])
        # Roboter Radius ist 10 cm
        self.radius = self.physik.radius

    # setzt den Roboter in Zustand Defekt und platziert ihn weit weg
    # (kann nur einmal aufgerufen werden. Danach muss der timeout ablaufen)
    def defekt(self, time):
        if self.physik.defekt:
            return
        self.defektTime = time
        self.physik.defekt = True
        self.moveto(10000, self.id * 10000, 0)

    # testet ob der Roboter nicht mehr defekt ist. (timeout vorbei)
    def isDefekt(self, time):
        if self.physik.defekt:
            if time - self.defektTime > gc.RULES["DefektTime"]:
                self.physik.defekt = False
                return False
        return True

    # setzt den Motorspeed
    def motorSpeed(self, a, b, c, d):
        self.physik.motorSpeed(a, b, c, d)

    # bewegt den Roboter an Position x,y mit der richtung d
    def moveto(self, x, y, d):
        self.physik.moveto(x, y, d)
        self.grafik.moveto(x, y, d)

    # Spieltick wird ausgefuehrt. Roboter Position wird aktualisiert
    def tick(self):
        if gc.ROBOTS[self.id-1]["Active"]:
            self.physik.tick()
            if gc.ROBOTS[self.id-1]["Stable"]:
                pass #TODO
            self.pos = np.array([self.physik.body.position.x,
                                 self.physik.body.position.y,
                                 self.physik.body.angle])
            self.orientation = np.rad2deg(self.pos[2])
        else:
            self.physik.moveto(1000, 1000*self.id, 0)

    # Zeichnet den Roboter
    def draw(self):
        if gc.ROBOTS[self.id-1]["Active"]:
            self.grafik.draw()

    # gibt True zurueck wenn der Roboter von diesem Object beruehrt wird
    def isPushedBy(self, _object):
        if type(_object) is Ball:
            return self.physik.isPushedByBall(_object.physik)
        else:
            return self.physik.isPushedByRobot(_object.physik)

    # gibt True zurueck wenn der Roboter nicht mehr im Spielfeld ist
    def isOutOfBounce(self):
        if self.physik.defekt:
            return False
        if self.pos[0] > (gc.INNER_FIELD_LENGTH / 2 + self.radius) or \
                        self.pos[0] < -(gc.INNER_FIELD_LENGTH / 2 + self.radius) or \
                        self.pos[1] > (gc.INNER_FIELD_WIDTH / 2 + self.radius) or \
                        self.pos[1] < -(gc.INNER_FIELD_WIDTH / 2 + self.radius):
            return True
        return False

    def isInStrafraum(self, seite):
        if seite is "links":
            if self.pos[0] > -20 + gc.INNER_FIELD_LENGTH / 2 and \
                            self.pos[0] < +gc.INNER_FIELD_LENGTH / 2 and \
                            self.pos[1] > -45 and \
                            self.pos[1] < 45:
                return True
            return False
        if seite is "rechts":
            if self.pos[0] < +20 - gc.INNER_FIELD_LENGTH / 2 and \
                            self.pos[0] > -gc.INNER_FIELD_LENGTH / 2 and \
                            self.pos[1] > -45 and \
                            self.pos[1] < 45:
                return True
            return False

    def getUS(self):
        return self.physik.getUS()





class Ball:
    def __init__(self, display, space):
        self.grafik = BallGrafik(display)
        self.physik = BallPhysik(space, self.grafik)
        # Ball Position in (x, y, rotation) Mittelpunkt ist x=0 y=0
        self.pos = np.array(self.physik.body.position)

    # Spieltick wird ausgefuerht
    def tick(self):
        self.physik.tick()
        self.pos = np.array(self.physik.body.position)

    # Setzt den Ball an Position x,y
    def moveto(self, x, y):
        self.physik.moveto(x, y)
        self.grafik.moveto(x, y)

    # Ball zeichnen
    def draw(self):
        self.grafik.draw()

    # Gibt True zurueck wenn der Ball sich bewegt Threshold ist 0.02.
    # kann man noch anpassen
    def isMoving(self):
        return np.linalg.norm(self.physik.body.velocity) > 0.02

    def kick(self,direction):
        self.physik.kick(direction)


class Field:
    def __init__(self, display, space):
        self.grafik = FeldGrafik(display)
        self.physik = FieldPhysik(space)

    # Wegen Kompatibilitaet?
    def tick(self):
        pass

    # Feld Zeichnen
    def draw(self):
        self.grafik.draw()

    # Spielstand updaten
    def setSpielstand(self, a, b):
        self.grafik.setSpielstand(a, b)

    # Zeit updaten
    def setTime(self, time):
        self.grafik.setTime(int(time))

    # gibt alle Schnittpunkte des Roboters robot mit der Auslinien
    # relativ zum Roboter wieder
    def getIntersectingPoints(self, robot):
        return self.physik.getIntersectingPoints(robot.physik)


class NeutralSpot:
    def __init__(self, _pos):
        self.pos = _pos

    # gibt die Distanz von dem objekt (ball oder roboter) zu dem neutralen Punkt
    def distance(self, object):
        return np.linalg.norm(self.pos - object.pos[0:2])

    # gibt True zurueck wenn einer der roboter in robots
    # oder der ball den neutralen Punkt besetzen
    def isOccupied(self, robots, ball):
        for robot in robots:
            d = np.linalg.norm(robot.pos[0:2] - self.pos)
            if d < 30:
                #self.refereeShout("occupied by robot")
                return True
        d = np.linalg.norm(ball.pos[0:2] - self.pos)
        if d < 5:
            #self.refereeShout("occupied by ball")
            return True
        return False


class Game:
    def __init__(self, _display):

        self.start_time = 0
        self.spielstand = [0, 0]
        self.isgoal = False
        self.wasTimeout = False
        self.wasGoal = False
        self.lastgoalteam = 0
        self.timeout = 0

        self.srRobot = 0
        self.time = 0
        self.balltimeout = 0
        self.display = _display

        self.space = pymunk.Space()
        self.space.damping = 0.998

        self.field = Field(self.display, self.space)

        self.ball = Ball(self.display, self.space)

        BLUE = 0, 0, 255
        RED = 255, 0, 0

        # init neutral spots
        self.nspots = [NeutralSpot((gc.INNER_FIELD_LENGTH / 2 - 45, gc.GOAL_WIDTH / 2)),
                       NeutralSpot((gc.INNER_FIELD_LENGTH / 2 - 45, -gc.GOAL_WIDTH / 2)),
                       NeutralSpot((-gc.INNER_FIELD_LENGTH / 2 + 45, gc.GOAL_WIDTH / 2)),
                       NeutralSpot((-gc.INNER_FIELD_LENGTH / 2 + 45, -gc.GOAL_WIDTH / 2)),
                       NeutralSpot((0, 0))]

        # init robots
        self.robots = [Robot(self.display, self.space, 1, BLUE, 180),
                       Robot(self.display, self.space, 2, BLUE, 180),
                       Robot(self.display, self.space, 3, RED, 0),
                       Robot(self.display, self.space, 4, RED, 0)]

        # move robot to starting position
        self.setzteRoboterUndBallAufStartPosition()

        self.ris = [robot_interface(self, self.robots[0], 180),
                        robot_interface(self, self.robots[1], 180),
                        robot_interface(self, self.robots[2], 0),
                        robot_interface(self, self.robots[3], 0)]

        self.ris[0].main = r1.main
        self.ris[1].main = r2.main
        self.ris[2].main = r3.main
        self.ris[3].main = r4.main

        for i in range(4):
            if gc.ROBOTS[i]["Active"]:
                robotRemote.init(self.ris[i])  # Roboter program initialisieren

        self.plotData = list()

    def refereeShout(self,text):
        print(str(self.time/1000)+" s Referee: " + text)

    # this function saves a dataset for ploting in the main thread.
    def plot(self,data):
        self.plotData = data

    def _physikTick(self,dt):
        for i in range(dt):
            self.space.step(1)  # Physik engine einen Tick weiter laufen lassen
            self.ball.tick()  # Ball updaten
            for robot in self.robots:
                robot.tick()  # Roboter updaten

    def _refereeTick(self,dt):
        for robot in self.robots:
            if gc.RULES["OutOfBounce"]:
                self.isOutOfBounce(robot)  # roboter auf OutofBounce testen
            if robot.isDefekt(self.time) is False:  # roboter auf nicht defekt testen
                self.setzteRobotwiederinsSpiel(robot)

        if gc.RULES["LagOfProgressActive"]:
            self.lagofProgress()  # Lag of Progress testen
        self.checkGoal()  # Tor testen
        if gc.RULES["DoubleDefense"]:
            self.doubleDefense()  # check double defense
        if gc.RULES["Pushing"]:
            self.pushing()  # check for pushing
        if self.isgoal:
            for robot in self.robots:# setzte alle Roboter auf nicht defekt
                robot.physik.defekt = False
            self.setzteRoboterUndBallAufStartPosition()
            self.isgoal = False
            self.wasGoal = True
            self.timeout = 0

        self.timeout = self.timeout + dt
        if self.timeout > gc.RULES["Timeout"] and gc.RULES["TimeoutActive"]:
            self.setzteRoboterUndBallAufStartPosition()
            self.timeout = 0
            self.wasTimeout = True

    def _otherTick(self,dt):
        # This is just a quick hack to plot some data
        if len(self.plotData) > 0:
            plt.plot(self.plotData)
            plt.show()
            self.plotData = list()
        # Zeitdisplay auf aktuelle Sekunden setzen
        self.field.setTime(self.time/1000)

    def _robotInterfaceTick(self,dt):
        for i in range(4):
            if gc.ROBOTS[i]["Active"]:
                robotRemote.tick(self.ris[i])  # Roboter sensorWerte updaten

    # calculate a tick in ms
    def tick(self, dt):
        self.time += dt  # Sielzeit hochzaelen in ms
        for i in range(dt):
            self._physikTick(1)
            self._robotInterfaceTick(1)
        self._otherTick(dt)
        self._refereeTick(dt)

        # Alle Objekte auf das Display zeichnen
    def draw(self):
        self.field.draw()
        self.ball.draw()
        for robot in self.robots:
            robot.draw()

    # schliest alle Threads die im Hintergrund laufen
    def shutdown(self):
        pass

    def restart(self):
        for robot in self.robots:
            robot.physik.defekt = False
        self.timeout = 0
        #self.spielstand = [0, 0]
        self.isgoal = False
        self.wasGoal = False
        self.wasTimeout = False
        self.lastgoalteam = 0
        self.srRobot = 0
        self.time = 0
        self.balltimeout = 0
        self.setzteRoboterUndBallAufStartPosition()
        self.refereeShout("restart Game")

    def setzteRoboterUndBallAufStartPosition(self):
        if gc.RULES["TestMode"] == 0:
            if self.lastgoalteam == 1:
                self.robots[0].moveto(13, random.gauss(0,2), 180)
                self.robots[1].moveto(80, random.gauss(0,2), 180)
                self.robots[2].moveto(-40,random.gauss(0,2), 0)
                self.robots[3].moveto(-80, random.gauss(0,2), 0)
            else:
                self.robots[0].moveto(40, random.gauss(0,2), 180)
                self.robots[1].moveto(80, random.gauss(0,2), 180)
                self.robots[2].moveto(-13, random.gauss(0,2), 0)
                self.robots[3].moveto(-80, random.gauss(0,2), 0)
            self.ball.moveto(0, 0)  # Ball in die Mitte legen
        if gc.RULES["TestMode"] == 1:
            self.setzteRobotaufNeutralenPunkt(self.robots[0])
            self.setzteRobotaufNeutralenPunkt(self.robots[1])
            self.setzteRobotaufNeutralenPunkt(self.robots[2])
            self.setzteRobotaufNeutralenPunkt(self.robots[3])
            self.setzteBallaufNeutralenPunkt()


    # setzt den Ball auf den naechsten neutralen Punkt, der nicht besetzt ist
    def setzteBallaufNeutralenPunkt(self):
        random.shuffle(self.nspots)
        bestspot = self.nspots[0]
        for nspot in self.nspots:
            if nspot.distance(self.ball) < bestspot.distance(self.ball) \
                    and not nspot.isOccupied(self.robots, self.ball):
                bestspot = nspot
        pos = bestspot.pos
        self.ball.moveto(pos[0], pos[1])

    # setzt den Roboter auf den naechsten neutralen Punkt, der nicht besetzt ist
    def setzteRobotaufNeutralenPunkt(self, robot:Robot):
        random.shuffle(self.nspots)
        bestspot = self.nspots[0]
        for nspot in self.nspots:
            if nspot.distance(robot) < bestspot.distance(robot) \
                    and not nspot.isOccupied(self.robots, self.ball):
                bestspot = nspot
        pos = bestspot.pos
        robot.moveto(pos[0], pos[1], robot.direction)

    # setzt den Roboter auf den neutralen Punkt,
    # der am weitesten vom Ball entfernt ist und nicht besetzt ist
    def setzteRobotwiederinsSpiel(self, robot:Robot):
        random.shuffle(self.nspots)
        bestspot = self.nspots[0]
        for nspot in self.nspots:
            if nspot.distance(self.ball) > bestspot.distance(self.ball) \
                    and not nspot.isOccupied(self.robots, self.ball):
                bestspot = nspot
        pos = bestspot.pos
        robot.moveto(pos[0], pos[1], robot.direction+180)

    # bei zu wenig Ballbewegung wird setzteBallaufNeutralenPunkt() ausgefuehrt
    def lagofProgress(self):
        if self.ball.isMoving():
            self.balltimeout = self.time
        if self.time - self.balltimeout > gc.RULES["LagOfProgress"]:
            self.refereeShout("lag of progress!!!")
            self.setzteBallaufNeutralenPunkt()
            self.balltimeout = self.time

    # wenn der Roboter ausserhalb vom Spielfeld steht wird er als defekt markiert
    # und verschwindet fuer 1 min aus dem Spiel
    def isOutOfBounce(self, robot:Robot):
        if robot.isOutOfBounce():
            for otherrobot in self.robots:
                if robot.isPushedBy(otherrobot) and otherrobot is not robot:
                    self.refereeShout("pushed out!!!")
                    self.setzteRobotaufNeutralenPunkt(robot)
                    return
            self.refereeShout("out of bounce!!!")
            robot.defekt(self.time)

    def pushing(self):
        for i in range(0, 2):
            if self.robots[i].isInStrafraum("links"):
                if self.robots[i].isPushedBy(self.robots[2]):
                    if self.robots[i].isPushedBy(self.ball) \
                            or self.robots[2].isPushedBy(self.ball):
                        self.refereeShout("pushing!!!")
                        self.setzteBallaufNeutralenPunkt()
                if self.robots[i].isPushedBy(self.robots[3]):
                    if self.robots[i].isPushedBy(self.ball) \
                            or self.robots[3].isPushedBy(self.ball):
                        self.refereeShout("pushing!!!")
                        self.setzteBallaufNeutralenPunkt()

        for i in range(2, 4):
            if self.robots[i].isInStrafraum("rechts"):
                if self.robots[i].isPushedBy(self.robots[0]):
                    if self.robots[i].isPushedBy(self.ball) \
                            or self.robots[0].isPushedBy(self.ball):
                        self.refereeShout("pushing!!!")
                        self.setzteBallaufNeutralenPunkt()
                if self.robots[i].isPushedBy(self.robots[1]):
                    if self.robots[i].isPushedBy(self.ball) \
                            or self.robots[1].isPushedBy(self.ball):
                        self.refereeShout("pushing!!!")
                        self.setzteBallaufNeutralenPunkt()

    def doubleDefense(self):
        if self.robots[0].isInStrafraum("links") and \
                self.robots[1].isInStrafraum("links"):
            d1 = np.linalg.norm(self.robots[0].pos[0:2] - self.ball.pos)
            d2 = np.linalg.norm(self.robots[1].pos[0:2] - self.ball.pos)
            self.refereeShout("double defense!!!")
            if d1 > d2:
                self.setzteRobotaufNeutralenPunkt(self.robots[0])
            else:
                self.setzteRobotaufNeutralenPunkt(self.robots[1])

        if self.robots[2].isInStrafraum("rechts") and \
                self.robots[3].isInStrafraum("rechts"):
            d1 = np.linalg.norm(self.robots[2].pos[0:2] - self.ball.pos)
            d2 = np.linalg.norm(self.robots[3].pos[0:2] - self.ball.pos)
            self.refereeShout("double defense!!!")
            if d1 > d2:
                self.setzteRobotaufNeutralenPunkt(self.robots[2])
            else:
                self.setzteRobotaufNeutralenPunkt(self.robots[3])

    def checkGoal(self):
        if self.ball.pos[0] < -gc.INNER_FIELD_LENGTH / 2 \
                and self.ball.pos[0] > -gc.INNER_FIELD_LENGTH / 2 - gc.GOAL_DEPTH \
                and self.ball.pos[1] > -gc.GOAL_WIDTH / 2 \
                and self.ball.pos[1] < gc.GOAL_WIDTH / 2:
            self.spielstand[0] = self.spielstand[0] + 1
            self.refereeShout("GOAL")
            self.isgoal = True
            self.lastgoalteam = 1

        if self.ball.pos[0] > gc.INNER_FIELD_LENGTH / 2 \
                and self.ball.pos[0] < gc.INNER_FIELD_LENGTH / 2 + gc.GOAL_DEPTH \
                and self.ball.pos[1] > -gc.GOAL_WIDTH / 2 \
                and self.ball.pos[1] < gc.GOAL_WIDTH / 2:
            self.spielstand[1] = self.spielstand[1] + 1
            self.refereeShout("GOAL")
            self.isgoal = True
            self.lastgoalteam = 2
        self.field.setSpielstand(self.spielstand[1], self.spielstand[0])

    def isTimeout(self):
        if self.wasTimeout:
            self.wasTimeout = False
            return True
        else:
            return False
