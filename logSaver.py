
# This is an optional logging of the sensor values of all robots.

#TODO robot state
#TODO goals numberOfLagofProgess..
#TODO saving in diffrent file formats

class Logger:
    def __init__(self, game):
        self._robotsProgramHandlers = game.robotProgramHandlers
        self._ball = game.ball
        self._robots = game.robots
        self._game = game
        self.loggingFlag = False
        self.DataSet = dict()

    def saveToFile(self,path):
        pass

    def startLogging(self):
        self.loggingFlag = True

    def stopLogging(self):
        self.loggingFlag = False

    def tick(self):
        if self.loggingFlag:
            ballPosition = self._ball.pos
            time = self._game.time
            self.DataSet[str(time)] = {"ballPosition": ballPosition}
            for id in range(4):
                position = self._robots[id].pos
                lb = self._robotsProgramHandlers[id].getLightBarrier()
                kompass = self._robotsProgramHandlers[id].getKompass()
                ball = self._robotsProgramHandlers[id].getIRBall()
                boden = self._robotsProgramHandlers[id].getBodenSensors()
                motors = self._robotsProgramHandlers[id]._motors
                blocks = self._robotsProgramHandlers[id].getPixy()
                self.DataSet[str(time)]["robot" + str(id)]={
                    "position": position,
                    "lb": lb,
                    "kompass": kompass,
                    "ball": ball,
                    "boden": boden,
                    "motors": motors,
                    "kompass": kompass,
                    "blocks": blocks}

