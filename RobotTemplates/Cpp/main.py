from robotRemote import RobotControl

def main(robot : RobotControl):

    while True:

        # Sensoren abfragen

        ballsensors = robot.getIRBall()
        kompass = robot.getKompass()
        boden = robot.getBodenSensors()
        ultraschall = robot.getUltraschall()

        # Fahren

        robot.setMotorSpeed(0,0,0,0)
