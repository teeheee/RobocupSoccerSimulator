
import importlib.util
from cputime import cputime
from grafik import *
from physik import *
from robotRemote import RobotControl

def loadRobotModule(path):
    robotSpec = importlib.util.spec_from_file_location("main", path)
    robotModule = importlib.util.module_from_spec(robotSpec)
    robotSpec.loader.exec_module(robotModule)
    return robotModule


class Robot:
    # display ist das pygame fenster
    # space ist der pymunk Raum
    # id is die Roboter ID
    # color ist die Farbe des Roboters
    def __init__(self, display, space, id, color ,playDirection):
        # stores the direction of the opponent goal
        self.playDirection = playDirection
        # grafik object
        self.grafik = RobotGraphic(display, id, color, playDirection)
        # physik object
        self.physik = RobotPhysik(space, self.grafik)
        # initial orientation
        self.orientation = playDirection
        # Roboter ID (setzt fest, welche Nummer auf dem Roboter steht)
        self.id = id
        # Roboter Position in (x, y, rotation) Mittelpunkt ist x=0 y=0
        self.pos = np.array([0, 0, 0])
        # Roboter Radius ist 10 cm
        self.radius = self.physik.radius

        self.isDefektFlag = False


    # setzt den Roboter in Zustand Defekt und platziert ihn weit weg
    # (kann nur einmal aufgerufen werden. Danach muss der timeout ablaufen)
    def setDefekt(self, state):
        self.physik.setDefekt(state)
        self.isDefektFlag = state

    # testet ob der Roboter nicht mehr defekt ist. (timeout vorbei)
    def isDefekt(self):
        return self.isDefektFlag

    # setzt den Motorspeed
    def motorSpeed(self, a, b, c, d):
        self.physik.motorSpeed(a, b, c, d)

    # bewegt den Roboter an Position x,y mit der richtung d
    def moveto(self, x, y, d):
        if gc.ROBOTS[self.id-1]["Active"]:
            self.physik.moveto(x, y, d)
            self.grafik.moveto(x, y, d)
            self.pos = np.array([self.physik.body.position.x,
                                 self.physik.body.position.y])

    # Spieltick wird ausgefuehrt. Roboter Position wird aktualisiert
    def tick(self):
        if gc.ROBOTS[self.id-1]["Active"]:
            if gc.ROBOTS[self.id-1]["Stable"]:
                self.physik.tick(True) #Rotation stable physics mode
            else:
                self.physik.tick(False) #unstable physics mode
            self.pos = np.array([self.physik.body.position.x,
                                 self.physik.body.position.y])
            self.orientation = np.rad2deg(self.physik.body.angle)
        else: # Robot inactive
            self.isDefektFlag = True
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
        if self.pos[0] > (gc.FIELD["TouchlineLength"] / 2 + self.radius) or \
                        self.pos[0] < -(gc.FIELD["TouchlineLength"] / 2 + self.radius) or \
                        self.pos[1] > (gc.FIELD["TouchlineWidth"] / 2 + self.radius) or \
                        self.pos[1] < -(gc.FIELD["TouchlineWidth"] / 2 + self.radius):
            return True
        return False

    def isInStrafraum(self, seite):
        if seite is "links":
            if self.pos[0] > -20 + gc.FIELD["TouchlineLength"] / 2 and \
                            self.pos[0] < +gc.FIELD["TouchlineLength"] / 2 and \
                            -45 < self.pos[1] and \
                            self.pos[1] < 45:
                return True
            return False
        if seite is "rechts":
            if self.pos[0] < +20 - gc.FIELD["TouchlineLength"] / 2 and \
                            self.pos[0] > -gc.FIELD["TouchlineLength"] / 2 and \
                            self.pos[1] > -45 and \
                            self.pos[1] < 45:
                return True
            return False



class Ball:
    def __init__(self, display, space):
        self.grafik = BallGraphic(display)
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
        self.pos = np.array(self.physik.body.position)

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
        self.grafik = FieldGraphic(display)
        self.physik = FieldPhysik(space)

    # Wegen Kompatibilitaet?
    def tick(self):
        pass

    # Feld Zeichnen
    def draw(self):
        self.grafik.draw()

    # Spielstand updaten
    def setScore(self, a, b):
        self.grafik.setScore(a, b)

    # Zeit updaten
    def setTime(self, time):
        self.grafik.setTime(int(time))


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
                #self._refereeShout("occupied by robot")
                return True
        d = np.linalg.norm(ball.pos - self.pos)
        if d < 5:
            #self._refereeShout("occupied by ball")
            return True
        return False


class Game:
    def __init__(self, _display):
        self.time = 0 #spielzeit in ms
        self.display = _display

        self.space = pymunk.Space()
        self.space.damping = 0.998

        self.debugOutput = DebugOutput(self.display)

        self.field = Field(self.display, self.space)

        self.ball = Ball(self.display, self.space)

        BLUE = 0, 0, 255
        RED = 255, 0, 0

        # init neutral spots
        self.nspots = [NeutralSpot((gc.FIELD["TouchlineLength"] / 2 - 45, gc.FIELD["GoalWidth"] / 2)),
                       NeutralSpot((gc.FIELD["TouchlineLength"]/ 2 - 45, -gc.FIELD["GoalWidth"] / 2)),
                       NeutralSpot((-gc.FIELD["TouchlineLength"] / 2 + 45, gc.FIELD["GoalWidth"] / 2)),
                       NeutralSpot((-gc.FIELD["TouchlineLength"] / 2 + 45, -gc.FIELD["GoalWidth"] / 2)),
                       NeutralSpot((0, 0))]

        # init robots
        self.robots = [Robot(self.display, self.space, 1, BLUE, 180),
                       Robot(self.display, self.space, 2, BLUE, 180),
                       Robot(self.display, self.space, 3, RED, 0),
                       Robot(self.display, self.space, 4, RED, 0)]


        self.referee = Referee(self)

        # move robot to starting position
        self.putEverythingOnStartPosition(1)

        self.robotInterfaceHandlers = [RobotInterface(self, 0),
                                        RobotInterface(self, 1),
                                        RobotInterface(self, 2),
                                        RobotInterface(self, 3)]

        robot1Module = loadRobotModule(gc.ROBOTS[0]["MainPath"])
        robot2Module = loadRobotModule(gc.ROBOTS[1]["MainPath"])
        robot3Module = loadRobotModule(gc.ROBOTS[2]["MainPath"])
        robot4Module = loadRobotModule(gc.ROBOTS[3]["MainPath"])

        # Roboter program initialisieren
        self.robotProgramHandlers = [ RobotControl(self.robotInterfaceHandlers[0],robot1Module),
                                      RobotControl(self.robotInterfaceHandlers[1],robot2Module),
                                      RobotControl(self.robotInterfaceHandlers[2],robot3Module),
                                      RobotControl(self.robotInterfaceHandlers[3],robot4Module)]


    def _physikTick(self,dt):
        for i in range(dt):
            self.space.step(1)  # Physik engine einen Tick weiter laufen lassen
            self.ball.tick()  # Ball updaten
            for robot in self.robots:
                robot.tick()  # Roboter updaten

    def _otherTick(self,dt):
        # Zeitdisplay auf aktuelle Sekunden setzen
        self.field.setTime(self.time/1000)

    def _robotInterfaceTick(self,dt):
        for i in range(4):
            if gc.ROBOTS[i]["Active"]:
                self.robotProgramHandlers[i].update(1)  # Roboter sensorWerte updaten

    # calculate a tick in ms
    def tick(self, dt):
        self.time += dt  # Sielzeit hochzaelen in ms
        cputime.printTimer("Rest")
        for i in range(dt):
            self._physikTick(1)
            cputime.printTimer("Physic")
            self._robotInterfaceTick(1)
            cputime.printTimer("robotInterfaceTick")
        self._otherTick(dt)
        cputime.printTimer("Other")
        self.referee.tick(dt)
        cputime.printTimer("Referee")

        # Alle Objekte auf das Display zeichnen
    def draw(self):
        self.field.draw()
        self.ball.draw()
        for robot in self.robots:
            robot.draw()
        self.debugOutput.draw()

    # schliest alle Threads die im Hintergrund laufen
    def shutdown(self):
        pass

    def restart(self):
        self.time = 0
        for robot in self.robots:
            robot.setDefekt(False)
        self.referee = Referee(self)
        self.putEverythingOnStartPosition(1)

    def putEverythingOnStartPosition(self,lastgoalteam):
        self.robots[0].setDefekt(False)
        self.robots[1].setDefekt(False)
        self.robots[2].setDefekt(False)
        self.robots[3].setDefekt(False)
        if gc.RULES["TestMode"] == 0:
            if lastgoalteam == 1:
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
            self.referee.putBallOnNeutralSpot()
            self.referee.putRobotOnNeutralSpot(self.robots[0])
            self.referee.putRobotOnNeutralSpot(self.robots[1])
            self.referee.putRobotOnNeutralSpot(self.robots[2])
            self.referee.putRobotOnNeutralSpot(self.robots[3])

    def end(self):
        self.restart()


class Referee:
    def __init__(self, game):
        self._game = game
        self._ballTimeout = 0
        self._wasGoal = False
        self._score = [0,0]
        self._lastGoalTeam = 1
        self._robots = game.robots
        self._ball = game.ball
        self._defektTimer = [0,0,0,0]

    def _refereeShout(self, string):
        print(str(self._game.time/100)+" s: Referee: "+string)


    def tick(self,dt):
        defectCounter = 0
        for robot in self._robots:
            if gc.RULES["OutOfBounce"] and gc.FIELD["TouchlineActive"]:
                if robot.isDefekt():
                    defectCounter = defectCounter + 1
                    if self._defektTimer[robot.id-1] < self._game.time:
                        robot.setDefekt(False)
                        self.putRobotOnNeutralSpot(robot)
                    if defectCounter == 4: # all robots are defekt ...
                        self._defektTimer = [0,0,0,0]
                        self._game.putEverythingOnStartPosition(self._lastGoalTeam)
                        self._refereeShout("all Robots Defekt restart!")

                else:
                    if self.isOutOfBounce(robot):  # roboter auf OutofBounce testen
                        self._defektTimer[robot.id-1] = self._game.time+gc.RULES["DefektTime"]
                        robot.setDefekt(True)
                        self._game.robotInterfaceHandlers[robot.id-1].setRobotState(State.OutOfBounce)


        if gc.RULES["LagOfProgressActive"]:
            self.lagofProgress()  # Lag of Progress testen
        self.checkGoal()  # Tor testen
        if gc.RULES["DoubleDefense"]:
            self.doubleDefense()  # check double defense
        if gc.RULES["Pushing"]:
            self.pushing()  # check for pushing
        if self._wasGoal:
            self._defektTimer = [0,0,0,0]
            for robot in self._robots:# setzte alle Roboter auf nicht defekt
                robot.setDefekt(False)
            self._game.putEverythingOnStartPosition(self._lastGoalTeam)
            self._wasGoal = False
            self._game.field.setScore(self._score[1], self._score[0])
            self._refereeShout("new Score" + str(self._score))

        if self._game.time > 60*10*1000:
            self._refereeShout("GAME OVER!!!")
            self._refereeShout("Score" + str(self._score))
            self._score = [0,0]
            self._defektTimer = [0,0,0,0]
            self._game.end()



    # setzt den Ball auf den naechsten neutralen Punkt, der nicht besetzt ist
    def putBallOnNeutralSpot(self):
        random.shuffle(self._game.nspots)
        bestspot = self._game.nspots[0]
        for nspot in self._game.nspots:
            if nspot.distance(self._game.ball) < bestspot.distance(self._game.ball) \
                    and not nspot.isOccupied(self._robots, self._game.ball):
                bestspot = nspot
        pos = bestspot.pos
        self._game.ball.moveto(pos[0], pos[1])

    # setzt den Roboter auf den naechsten neutralen Punkt,
    # der am weitesten vom Ball entfernt ist und nicht besetzt ist
    def putRobotOnNeutralSpot(self, robot:Robot):
        random.shuffle(self._game.nspots)
        bestspot = self._game.nspots[0]
        for nspot in self._game.nspots:
            if nspot.distance(self._game.ball) > bestspot.distance(self._game.ball) \
                    and not nspot.isOccupied(self._robots, self._ball):
                bestspot = nspot
        pos = bestspot.pos
        if robot.id == 1:
            print("---------")
            print("ball: " + str(self._ball.pos))
            print("robot: " + str(pos))
            print("---------")
        robot.moveto(pos[0], pos[1], robot.playDirection)

    # bei zu wenig Ballbewegung wird putBallOnNeutralSpot() ausgefuehrt
    def lagofProgress(self):
        if self._game.ball.isMoving():
            self._ballTimeout = self._game.time
        if self._game.time - self._ballTimeout > gc.RULES["LagOfProgress"]:
            self._refereeShout("lag of progress!!!")
            self.putBallOnNeutralSpot()
            self._ballTimeout = self._game.time

    # wenn der Roboter ausserhalb vom Spielfeld steht wird er als defekt markiert
    # und verschwindet fuer 1 min aus dem Spiel
    def isOutOfBounce(self, robot:Robot):
        if robot.isOutOfBounce():
            for otherrobot in self._robots:
                if robot.isPushedBy(otherrobot) and otherrobot is not robot:
                    self._refereeShout("pushed out!!!")
                    self.putRobotOnNeutralSpot(robot)
                    return False
            self._refereeShout("out of bounce!!!")
            return True
        return False

    def pushing(self):
        for i in range(0, 2):
            if self._robots[i].isInStrafraum("links"):
                if self._robots[i].isPushedBy(self._robots[2]):
                    if self._robots[i].isPushedBy(self._ball) \
                            or self._robots[2].isPushedBy(self._ball):
                        self._refereeShout("pushing!!!")
                        self.putBallOnNeutralSpot()
                if self._robots[i].isPushedBy(self._robots[3]):
                    if self._robots[i].isPushedBy(self._ball) \
                            or self._robots[3].isPushedBy(self._ball):
                        self._refereeShout("pushing!!!")
                        self.putBallOnNeutralSpot()

        for i in range(2, 4):
            if self._robots[i].isInStrafraum("rechts"):
                if self._robots[i].isPushedBy(self._robots[0]):
                    if self._robots[i].isPushedBy(self._ball) \
                            or self._robots[0].isPushedBy(self._ball):
                        self._refereeShout("pushing!!!")
                        self.putBallOnNeutralSpot()
                if self._robots[i].isPushedBy(self._robots[1]):
                    if self._robots[i].isPushedBy(self._ball) \
                            or self._robots[1].isPushedBy(self._ball):
                        self._refereeShout("pushing!!!")
                        self.putBallOnNeutralSpot()

    def doubleDefense(self):
        if self._robots[0].isInStrafraum("links") and \
                self._robots[1].isInStrafraum("links"):
            d1 = np.linalg.norm(self._robots[0].pos - self._ball.pos)
            d2 = np.linalg.norm(self._robots[1].pos - self._ball.pos)
            self._refereeShout("double defense!!!")
            if d1 > d2:
                self.putRobotOnNeutralSpot(self._robots[0])
            else:
                self.putRobotOnNeutralSpot(self._robots[1])

        if self._robots[2].isInStrafraum("rechts") and \
                self._robots[3].isInStrafraum("rechts"):
            d1 = np.linalg.norm(self._robots[2].pos - self._ball.pos)
            d2 = np.linalg.norm(self._robots[3].pos - self._ball.pos)
            self._refereeShout("double defense!!!")
            if d1 > d2:
                self.putRobotOnNeutralSpot(self._robots[2])
            else:
                self.putRobotOnNeutralSpot(self._robots[3])

    def checkGoal(self):
        if -gc.FIELD["TouchlineLength"] / 2 > self._ball.pos[0] \
                and self._ball.pos[0] > -gc.FIELD["TouchlineLength"] / 2 - gc.FIELD["GoalDepth"] \
                and self._ball.pos[1] > -gc.FIELD["GoalWidth"] / 2 \
                and self._ball.pos[1] < gc.FIELD["GoalWidth"] / 2:
            self._score[0] += 1
            self._lastGoalTeam = 1
            self._refereeShout("GOAL")
            self._game.robotInterfaceHandlers[0].setRobotState(State.OwnGoal)
            self._game.robotInterfaceHandlers[1].setRobotState(State.OwnGoal)
            self._game.robotInterfaceHandlers[2].setRobotState(State.OponentGoal)
            self._game.robotInterfaceHandlers[3].setRobotState(State.OponentGoal)
            self._wasGoal = True

        if gc.FIELD["TouchlineLength"] / 2 < self._ball.pos[0] \
                and self._ball.pos[0] < gc.FIELD["TouchlineLength"] / 2 + gc.FIELD["GoalDepth"] \
                and self._ball.pos[1] > -gc.FIELD["GoalWidth"] / 2 \
                and self._ball.pos[1] < gc.FIELD["GoalWidth"] / 2:
            self._score[1] += 1
            self._refereeShout("GOAL")
            self._game.robotInterfaceHandlers[2].setRobotState(State.OwnGoal)
            self._game.robotInterfaceHandlers[3].setRobotState(State.OwnGoal)
            self._game.robotInterfaceHandlers[0].setRobotState(State.OponentGoal)
            self._game.robotInterfaceHandlers[1].setRobotState(State.OponentGoal)
            self._wasGoal = True
            self._lastGoalTeam = 0