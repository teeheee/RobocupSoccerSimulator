from grafik import *
from physik import *
import pymunk

import Team1.robot1.robotRemote as r1
import Team1.robot2.robotRemote as r2
import Team2.robot1.robotRemote as r3
import Team2.robot2.robotRemote as r4


class Robot:
    # display ist das pygame fenster
    # space ist der pymunk Raum
    # _id is die Roboter ID
    # color ist die Farbe des Roboters
    def __init__(self, display, space, _id, color ,direction):
        self.direction = direction
        self.grafik = RobotGrafik(display, _id, color, direction)  # Physik
        self.physik = RobotPhysik(space, self.grafik)
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
        if d < 20:
            print("occupied by ball")
            return True
        return False


class Game:
    def __init__(self, _display):
        self.spielstand = [0, 0]
        self.isgoal = False

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

        self.robots = [Robot(self.display, self.space, 1, BLUE, 180),
                       Robot(self.display, self.space, 2, BLUE, 180),
                       Robot(self.display, self.space, 3, RED,    0),
                       Robot(self.display, self.space, 4, RED,    0)]

        # Todo flexible starting Position
        self.robots[0].moveto(13, 1, 180)
        self.robots[1].moveto(80, -1, 180)
        self.robots[2].moveto(-40, 3, 0)
        self.robots[3].moveto(-80, 2, 0)

        self.nspots = [NeutralSpot((gc.INNER_FIELD_LENGTH / 2 - 45, gc.GOAL_WIDTH / 2)),
                       NeutralSpot((gc.INNER_FIELD_LENGTH / 2 - 45, -gc.GOAL_WIDTH / 2)),
                       NeutralSpot((-gc.INNER_FIELD_LENGTH / 2 + 45, gc.GOAL_WIDTH / 2)),
                       NeutralSpot((-gc.INNER_FIELD_LENGTH / 2 + 45, -gc.GOAL_WIDTH / 2)),
                       NeutralSpot((0, 0))]


        self.ris = [robot_interface(self, self.robots[0], 180),
                        robot_interface(self, self.robots[1], 180),
                        robot_interface(self, self.robots[2], 0),
                        robot_interface(self, self.robots[3], 0)]


    def tick(self, dt): #TODO make it faster somehow....
        self.time += dt  # Sielzeit hochzaelen
        self.space.step(dt)  # Physik engine einen Tick weiter laufen lassen
        self.ball.tick()  # Ball updaten
        for robot in self.robots:
            robot.tick()  # Roboter updaten
            self.isOutOfBounce(robot)  # roboter auf OutofBounce testen
            if robot.isDefekt(self.time) is False:  # roboter auf nicht defekt testen
                self.setzteRobotaufNeutralenPunkt(robot)  # TODO kann man schoner machen

        self.lagofProgress()  # Lag of Progress testen
        self.checkGoal()  # Tor testen
        self.doubleDefense()  # check double defense
        self.pushing()  # check for pushing
        if self.isgoal:  # TODO Startposition variabel?
            for robot in self.robots:
                robot.physik.defekt = False
            self.robots[0].moveto(13, 1, 180)
            self.robots[1].moveto(80, -1, 180)
            self.robots[2].moveto(-40, 1, 0)
            self.robots[3].moveto(-80, -1, 0)
            self.ball.moveto(0, 0)  # Ball in die Mitte legen
            self.isgoal = False

        self.srRobot = self.srRobot + 1 #Sampling rate for the Robot
        if self.srRobot > 20:
            r1.tick(self.ris[0])  # Roboter program laufen lassen
            r2.tick(self.ris[1])  # Roboter program laufen lassen
            r3.tick(self.ris[2])  # Roboter program laufen lassen
            r4.tick(self.ris[3])  # Roboter program laufen lassen
            self.srRobot = 0

        # Alle Objekte auf das Display zeichnen
    def draw(self): #TODO make it faster somehow....
        self.field.draw()
        self.ball.draw()
        for robot in self.robots:
            robot.draw()

    # schliest alle Threads die im Hintergrund laufen
    def shutdown(self):
        pass

    # setzt den Ball auf den naechsten neutralen Punkt, der nicht besetzt ist
    def setzteBallaufNeutralenPunkt(self):
        bestspot = self.nspots[0]
        for nspot in self.nspots:
            if nspot.distance(self.ball) < bestspot.distance(self.ball) \
                    and not nspot.isOccupied(self.robots, self.ball):
                bestspot = nspot
        pos = bestspot.pos
        self.ball.moveto(pos[0], pos[1])

    # setzt den Roboter auf den naechsten neutralen Punkt, der nicht besetzt ist
    def setzteRobotaufNeutralenPunkt(self, robot):
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
        bestspot = self.nspots[0]
        for nspot in self.nspots:
            if nspot.distance(self.ball) > bestspot.distance(self.ball) \
                    and not nspot.isOccupied(self.robots, self.ball):
                bestspot = nspot
        pos = bestspot.pos
        robot.moveto(pos[0], pos[1], robot.direction)

    # bei zu wenig Ballbewegung wird setzteBallaufNeutralenPunkt() ausgefuehrt
    def lagofProgress(self):
        if self.ball.isMoving():
            self.balltimeout = self.time
        if self.time - self.balltimeout > 2000:
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

        if self.ball.pos[0] > gc.INNER_FIELD_LENGTH / 2 \
                and self.ball.pos[0] < gc.INNER_FIELD_LENGTH / 2 + gc.GOAL_DEEP \
                and self.ball.pos[1] > -gc.GOAL_WIDTH / 2 \
                and self.ball.pos[1] < gc.GOAL_WIDTH / 2:
            self.spielstand[1] = self.spielstand[1] + 1
            print("GOAL")
            self.isgoal = True
        self.field.setSpielstand(self.spielstand[1], self.spielstand[0])
