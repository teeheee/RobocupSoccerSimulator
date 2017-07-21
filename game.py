

import Team1.robot1.main as r1
import Team1.robot2.main as r2
import Team2.robot1.main as r3
import Team2.robot2.main as r4
import robotRemote
import time
from grafik import *
from physik import *


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
            if time - self.defektTime > 24000:
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
        self.physik.tick()
        self.pos = np.array([self.physik.body.position.x,
                             self.physik.body.position.y,
                             self.physik.body.angle])
        self.orientation = np.rad2deg(self.pos[2])

    # Zeichnet den Roboter
    def draw(self):
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
                print("occupied by robot")
                return True
        d = np.linalg.norm(ball.pos[0:2] - self.pos)
        if d < 5:
            print("occupied by ball")
            return True
        return False


class Game:
    def __init__(self, _display):
        self.spielstand = [0, 0]
        self.isgoal = False
        self.lastgoalteam = 0

        self.lagofprogressTimeout = 2000

        self.srRobot = 0
        self.time = 0
        self.balltimeout = 0
        self.display = _display

        self.space = pymunk.Space()
        self.space.damping = 0.995

        self.field = Field(self.display, self.space)

        self.ball = Ball(self.display, self.space)

        BLUE = 0, 0, 255
        RED = 255, 0, 0
        DEEPPINK = 255,20,147

        self.nspots = [NeutralSpot((gc.INNER_FIELD_LENGTH / 2 - 45, gc.GOAL_WIDTH / 2)),
                       NeutralSpot((gc.INNER_FIELD_LENGTH / 2 - 45, -gc.GOAL_WIDTH / 2)),
                       NeutralSpot((-gc.INNER_FIELD_LENGTH / 2 + 45, gc.GOAL_WIDTH / 2)),
                       NeutralSpot((-gc.INNER_FIELD_LENGTH / 2 + 45, -gc.GOAL_WIDTH / 2)),
                       NeutralSpot((0, 0))]

        self.robots = [Robot(self.display, self.space, 1, BLUE, 180),
                       Robot(self.display, self.space, 2, BLUE, 180),
                       Robot(self.display, self.space, 3, DEEPPINK,    0),
                       Robot(self.display, self.space, 4, RED,    0)]

        self.robots[0].moveto(13, random.gauss(0,2), 180)
        self.robots[1].moveto(80, random.gauss(0,2), 180)
        self.robots[2].moveto(-40, random.gauss(0,2), 0)
        self.robots[3].moveto(-80, random.gauss(0,2), 0)



        self.ris = [robot_interface(self, self.robots[0], 180),
                        robot_interface(self, self.robots[1], 180),
                        robot_interface(self, self.robots[2], 0),
                        robot_interface(self, self.robots[3], 0)]

        self.ris[0].main = r1.main
        self.ris[1].main = r2.main
        self.ris[2].main = r3.main
        self.ris[3].main = r4.main

        robotRemote.init(self.ris[0])  # Roboter program initialisieren
        robotRemote.init(self.ris[1])  # Roboter program initialisieren
        robotRemote.init(self.ris[2])  # Roboter program initialisieren
        robotRemote.init(self.ris[3])  # Roboter program initialisieren


    def tick(self, dt):
        self.time += dt  # Sielzeit hochzaelen
        self.space.step(dt)  # Physik engine einen Tick weiter laufen lassen
        self.ball.tick()  # Ball updaten
        for robot in self.robots:
            robot.tick()  # Roboter updaten
            self.isOutOfBounce(robot)  # roboter auf OutofBounce testen
            if robot.isDefekt(self.time) is False:  # roboter auf nicht defekt testen
                self.setzteRobotwiederinsSpiel(robot)


        self.lagofProgress()  # Lag of Progress testen
        self.checkGoal()  # Tor testen
        self.doubleDefense()  # check double defense
        self.pushing()  # check for pushing


        self.srRobot = self.srRobot + 1 #Sampling rate for the Robot
        if self.srRobot > 20 or self.isgoal:
            robotRemote.tick(self.ris[0])  # Roboter program initialisieren
            robotRemote.tick(self.ris[1])  # Roboter program initialisieren
            robotRemote.tick(self.ris[2])  # Roboter program initialisieren
            robotRemote.tick(self.ris[3])  # Roboter program initialisieren
            self.srRobot = 0

#### DELETE THIS BLOCK FOR NORMAL GAME PLAY. Just for faster learining.... ;-)

        self.robots[0].defekt(self.time)
        self.robots[1].defekt(self.time)
        self.robots[3].defekt(self.time)


        self.lagofprogressTimeout = 5000

        if self.robots[2].physik.defekt == True:
            robotRemote.tick(self.ris[2])
            time.sleep(1)
            self.robots[2].physik.defekt = False
            self.setzteRobotwiederinsSpiel(self.robots[2])
###########ENBLOCK


        if self.isgoal:
            time.sleep(1)
            for robot in self.robots:
                robot.physik.defekt = False
            if self.lastgoalteam == 2:
                self.robots[0].moveto(13, random.gauss(0, 2), 180)
                self.robots[1].moveto(80, random.gauss(0, 2), 180)
                self.robots[2].moveto(-40, random.gauss(0, 2), 0)
                self.robots[3].moveto(-80, random.gauss(0, 2), 0)
            if self.lastgoalteam == 1:
                self.robots[0].moveto(40, random.gauss(0, 2), 180)
                self.robots[1].moveto(80, random.gauss(0, 2), 180)
                self.robots[2].moveto(-13, random.gauss(0, 2), 0)
                self.robots[3].moveto(-80, random.gauss(0, 2), 0)
            self.ball.moveto(0, 0)  # Ball in die Mitte legen
            self.isgoal = False
        # Alle Objekte auf das Display zeichnen
    def draw(self):
        self.field.draw()
        self.ball.draw()
        for robot in self.robots:
            robot.draw()

    # schliest alle Threads die im Hintergrund laufen
    def shutdown(self):
        pass

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
    def setzteRobotaufNeutralenPunkt(self, robot):
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
    def setzteRobotwiederinsSpiel(self, robot):
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
        if self.time - self.balltimeout > self.lagofprogressTimeout:
            print("lag of progress!!!")
            self.setzteBallaufNeutralenPunkt()
            self.balltimeout = self.time

    # wenn der Roboter ausserhalb vom Spielfeld steht wird er als defekt markiert
    # und verschwindet fuer 1 min aus dem Spiel
    def isOutOfBounce(self, robot):
        if robot.isOutOfBounce():
            for otherrobot in self.robots:
                if robot.isPushedBy(otherrobot) and otherrobot is not robot:
                    print("pushed out!!!")
                    self.setzteRobotaufNeutralenPunkt(robot)
                    return
            print("out of bounce!!!")
            robot.defekt(self.time)

    def pushing(self):
        for i in range(0, 2):
            if self.robots[i].isInStrafraum("links"):
                if self.robots[i].isPushedBy(self.robots[2]):
                    if self.robots[i].isPushedBy(self.ball) \
                            or self.robots[2].isPushedBy(self.ball):
                        print("pushing!!!")
                        self.setzteBallaufNeutralenPunkt()
                if self.robots[i].isPushedBy(self.robots[3]):
                    if self.robots[i].isPushedBy(self.ball) \
                            or self.robots[3].isPushedBy(self.ball):
                        print("pushing!!!")
                        self.setzteBallaufNeutralenPunkt()

        for i in range(2, 4):
            if self.robots[i].isInStrafraum("rechts"):
                if self.robots[i].isPushedBy(self.robots[0]):
                    if self.robots[i].isPushedBy(self.ball) \
                            or self.robots[0].isPushedBy(self.ball):
                        print("pushing!!!")
                        self.setzteBallaufNeutralenPunkt()
                if self.robots[i].isPushedBy(self.robots[1]):
                    if self.robots[i].isPushedBy(self.ball) \
                            or self.robots[1].isPushedBy(self.ball):
                        print("pushing!!!")
                        self.setzteBallaufNeutralenPunkt()

    def doubleDefense(self):
        if self.robots[0].isInStrafraum("links") and \
                self.robots[1].isInStrafraum("links"):
            d1 = np.linalg.norm(self.robots[0].pos[0:2] - self.ball.pos)
            d2 = np.linalg.norm(self.robots[1].pos[0:2] - self.ball.pos)
            print("double defense!!!")
            if d1 > d2:
                self.setzteRobotaufNeutralenPunkt(self.robots[0])
            else:
                self.setzteRobotaufNeutralenPunkt(self.robots[1])

        if self.robots[2].isInStrafraum("rechts") and \
                self.robots[3].isInStrafraum("rechts"):
            d1 = np.linalg.norm(self.robots[2].pos[0:2] - self.ball.pos)
            d2 = np.linalg.norm(self.robots[3].pos[0:2] - self.ball.pos)
            print("double defense!!!")
            if d1 > d2:
                self.setzteRobotaufNeutralenPunkt(self.robots[2])
            else:
                self.setzteRobotaufNeutralenPunkt(self.robots[3])

    def checkGoal(self):
        if self.ball.pos[0] < -gc.INNER_FIELD_LENGTH / 2 \
                and self.ball.pos[0] > -gc.INNER_FIELD_LENGTH / 2 - gc.GOAL_DEEP \
                and self.ball.pos[1] > -gc.GOAL_WIDTH / 2 \
                and self.ball.pos[1] < gc.GOAL_WIDTH / 2:
            self.spielstand[0] = self.spielstand[0] + 1
            print("GOAL")
            self.isgoal = True
            self.lastgoalteam = 1

        if self.ball.pos[0] > gc.INNER_FIELD_LENGTH / 2 \
                and self.ball.pos[0] < gc.INNER_FIELD_LENGTH / 2 + gc.GOAL_DEEP \
                and self.ball.pos[1] > -gc.GOAL_WIDTH / 2 \
                and self.ball.pos[1] < gc.GOAL_WIDTH / 2:
            self.spielstand[1] = self.spielstand[1] + 1
            print("GOAL")
            self.isgoal = True
            self.lastgoalteam = 2
        self.field.setSpielstand(self.spielstand[1], self.spielstand[0])
