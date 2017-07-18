import numpy as np
import gameconfig as gc
from interface import *
from pymunk import *
import pymunk

collision_types = {
    "ball": 1,
    "robot": 2,
    "tor": 3,
    "auslinie": 4
}

#TODO more comments

class RobotPhysik:
    def __init__(self, _space, _robotgrafik):
        self.robotgrafik = _robotgrafik
        self.space = _space
        self.radius = 10
        self.mass = 2000
        self.vmax = 10
        self.fmax = 100
        self.motor = np.array([0, 0, 0, 0])
        self.defekt = False

        self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius, (0, 0)))
        self.body.position = ((self.robotgrafik.x_position, self.robotgrafik.y_position))
        self.body.angle = np.radians(self.robotgrafik.orientation)

        polygonlist1 = [[3,5],[5,3],[3,1],[3,-1],[-5,-1],[-5,3],[-3,5]]
        polygonlist2 = [[3,1],[5,-3],[3,-5],[-3,-5],[-5,-3],[-5,1]]
        scale = 10 / 5.83
        newpolygon1 = []
        for p in polygonlist1:
            newpolygon1.append([p[0]*scale,p[1]*scale])
        newpolygon2 = []
        for p in polygonlist2:
                newpolygon2.append([p[0] * scale, p[1] * scale])

        self.shape1 = pymunk.Poly(self.body, newpolygon1)
        self.shape1.elasticity = 0
        self.shape1.friction = 0.9
        self.shape1.collision_type = collision_types["robot"]
        self.shape2 = pymunk.Poly(self.body, newpolygon2)
        self.shape2.elasticity = 0
        self.shape2.friction = 0.9
        self.shape2.collision_type = collision_types["robot"]

        self.shape3 = pymunk.Circle(self.body,7)

        self.space.add(self.body, self.shape1 ,self.shape2,self.shape3)

    def motorSpeed(self, a, b, c, d):
        self.motor = np.array([a, b, c, d])

    def moveto(self, x, y, d):
        self.body.position = (x, y)
        self.body.angle = np.radians(d)
        self.space.reindex_shapes_for_body(self.body)

    def tick(self): #TODO better omniwheel Physics
        if self.defekt:
            self.motor = np.array([0, 0, 0, 0])
            self.body.torque = 0
            self.body.force = (0, 0)
        else:
            self.robotgrafik.moveto((self.body.position.x), (self.body.position.y), -np.degrees(self.body.angle))
            A = np.array([[1, 0, -1, 0], [0, 1, 0, -1], [10, 10, 10, 10]])
            f = A.dot(self.motor)
            theta = self.body.angle -  np.radians(45+180)
            c, s = np.cos(theta), np.sin(theta)
            R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
            v = np.array([self.body.velocity[0], self.body.velocity[1], self.body.angular_velocity])
            f = R.dot(f)
            f_soll = (f - (self.fmax / self.vmax) * v)
            self.body.torque = f_soll[2]
            self.body.force = tuple(f_soll[0:2])

    def isPushedByRobot(self, robot):
        p1 = self.shape1.shapes_collide(robot.shape1)
        p2 = self.shape1.shapes_collide(robot.shape2)
        p3 = self.shape2.shapes_collide(robot.shape1)
        p4 = self.shape2.shapes_collide(robot.shape2)
        if len(p1.points) > 0 or len(p2.points) > 0 or len(p3.points) > 0 or len(p4.points) > 0:
            return True
        return False

    def isPushedByBall(self, ball):
        p1 = self.shape1.shapes_collide(ball.shape)
        p2 = self.shape2.shapes_collide(ball.shape)
        if len(p1.points) > 0 or len(p2.points) > 0:
            return True
        return False


class BallPhysik:
    def __init__(self, _space, _ballgrafik):
        self.space = _space
        self.ballgrafik = _ballgrafik

        self.radius = 3
        self.mass = 80
        self.pos = np.array((self.ballgrafik.x_position, self.ballgrafik.y_position))

        self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius, (0, 0)))
        self.body.position = ((self.ballgrafik.x_position, self.ballgrafik.y_position))

        self.shape = pymunk.Circle(self.body, self.radius, (0, 0))
        self.shape.elasticity = 0.95
        self.shape.friction = 1
        self.shape.collision_type = collision_types["ball"]

        self.space.add(self.body, self.shape)

    def moveto(self, x, y):
        self.body.position = (x, y)
        self.body.velocity = (0, 0)
        self.space.reindex_shapes_for_body(self.body)

    def tick(self):
        self.ballgrafik.moveto((self.body.position.x), (self.body.position.y))


class FieldPhysik:
    def __init__(self, _space):
        self.space = _space

        # Walls
        static_body = self.space.static_body
        static_lines = [pymunk.Segment(static_body, (-gc.OUTER_FIELD_LENGTH / 2, -gc.OUTER_FIELD_WIDTH / 2),
                                       (-gc.OUTER_FIELD_LENGTH / 2, gc.OUTER_FIELD_WIDTH / 2), 0.0)
            , pymunk.Segment(static_body, (-gc.OUTER_FIELD_LENGTH / 2, -gc.OUTER_FIELD_WIDTH / 2),
                             (gc.OUTER_FIELD_LENGTH / 2, -gc.OUTER_FIELD_WIDTH / 2), 0.0)
            , pymunk.Segment(static_body, (gc.OUTER_FIELD_LENGTH / 2, gc.OUTER_FIELD_WIDTH / 2),
                             (-gc.OUTER_FIELD_LENGTH / 2, gc.OUTER_FIELD_WIDTH / 2), 0.0)
            , pymunk.Segment(static_body, (gc.OUTER_FIELD_LENGTH / 2, gc.OUTER_FIELD_WIDTH / 2),
                             (gc.OUTER_FIELD_LENGTH / 2, -gc.OUTER_FIELD_WIDTH / 2), 0.0)]
        for line in static_lines:
            line.elasticity = 0.95
            line.friction = 0.9
        self.space.add(static_lines)

        self.tor = TorPhysik(self.space)

        # Auslinien
        static_body = self.space.static_body
        self.auslinien = [pymunk.Segment(static_body, (-gc.INNER_FIELD_LENGTH / 2, -gc.INNER_FIELD_WIDTH / 2),
                                         (-gc.INNER_FIELD_LENGTH / 2, gc.INNER_FIELD_WIDTH / 2), 0.0)
            , pymunk.Segment(static_body, (-gc.INNER_FIELD_LENGTH / 2, -gc.INNER_FIELD_WIDTH / 2),
                             (gc.INNER_FIELD_LENGTH / 2, -gc.INNER_FIELD_WIDTH / 2), 0.0)
            , pymunk.Segment(static_body, (gc.INNER_FIELD_LENGTH / 2, gc.INNER_FIELD_WIDTH / 2),
                             (-gc.INNER_FIELD_LENGTH / 2, gc.INNER_FIELD_WIDTH / 2), 0.0)
            , pymunk.Segment(static_body, (gc.INNER_FIELD_LENGTH / 2, gc.INNER_FIELD_WIDTH / 2),
                             (gc.INNER_FIELD_LENGTH / 2, -gc.INNER_FIELD_WIDTH / 2), 0.0)]

        for linie in self.auslinien:
            linie.collision_type = collision_types["auslinie"]
            linie.sensor = True

        self.space.add(self.auslinien)

    def tick(self):
        pass

    def getIntersectingPoints(self, robot):
        points = []
        for linie in self.auslinien:
            p = linie.shapes_collide(robot.shape3)
            if len(p.points) > 0:
                points.append(p.points[0].point_a - robot.body.position)
                points.append(p.points[0].point_b - robot.body.position)
        return points


class TorPhysik:
    def __init__(self, _space):
        self.isgoal = False
        self.space = _space
        static_body = self.space.static_body
        static_lines_tor1 = [pymunk.Segment(static_body, (gc.INNER_FIELD_LENGTH / 2, gc.GOAL_WIDTH / 2) 		, (gc. INNER_FIELD_LENGTH / 2+gc.GOAL_DEEP,gc. GOAL_WIDTH/2) ,0.0),
                             pymunk.Segment(static_body, (gc.INNER_FIELD_LENGTH / 2 + gc.GOAL_DEEP, gc.GOAL_WIDTH / 2),
                                            (gc.
                                             INNER_FIELD_LENGTH / 2 + gc.GOAL_DEEP, -gc.GOAL_WIDTH / 2), 0.0)
            , pymunk.
                                 Segment(static_body, (gc.INNER_FIELD_LENGTH / 2 + gc.GOAL_DEEP, -gc.GOAL_WIDTH / 2), (
                gc.INNER_FIELD_LENGTH / 2, -gc.GOAL_WIDTH / 2), 0.0)]
        static_lines_tor2 = [pymunk.Segment(static_body, (-gc.INNER_FIELD_LENGTH / 2, gc.GOAL_WIDTH / 2) 		, (-gc. INNER_FIELD_LENGTH / 2-gc.GOAL_DEEP,gc. GOAL_WIDTH/2) ,0.0),
                             pymunk.Segment(static_body, (-gc.INNER_FIELD_LENGTH / 2 - gc.GOAL_DEEP, gc.GOAL_WIDTH / 2),
                                            (- gc.
                                             INNER_FIELD_LENGTH / 2 - gc.GOAL_DEEP, -gc.GOAL_WIDTH / 2), 0.0)
            , pymunk.
                                 Segment(static_body, (-gc.INNER_FIELD_LENGTH / 2 - gc.GOAL_DEEP, -gc.GOAL_WIDTH / 2),
                                         (-
                                          gc.INNER_FIELD_LENGTH / 2, -gc.GOAL_WIDTH / 2), 0.0)]
        tor_balken_1 = pymunk.Segment(static_body, (gc.INNER_FIELD_LENGTH / 2, -gc.GOAL_WIDTH / 2), (
            gc.INNER_FIELD_LENGTH / 2, gc.GOAL_WIDTH / 2), 0.0)
        tor_balken_2 = pymunk.Segment(static_body, (-gc.INNER_FIELD_LENGTH / 2, -gc.GOAL_WIDTH / 2), (
            -gc.INNER_FIELD_LENGTH / 2, gc.GOAL_WIDTH / 2), 0.0)

        for line in static_lines_tor1:
            line.elasticity = 0.95
            line.friction = 0.9
        for line in static_lines_tor2:
            line.elasticity = 0.95
            line.friction = 0.9
        self.space.add(static_lines_tor1)
        self.space.add(static_lines_tor2)

        tor_balken_1.collision_type = collision_types["tor"]
        tor_balken_2.collision_type = collision_types["tor"]
        #TODO Torbalken sollte wieder funktionieren...
        # def nurball(arbiter, space, data):
        #     return False
        #
        # def nurroboter(arbiter, space, data):
        #     return True
        #
        # h1 = self.space.add_collision_handler(collision_types["ball"], collision_types["tor"])
        # h1.begin = nurball
        # h2 = self.space.add_collision_handler(collision_types["robot"], collision_types["tor"])
        # h2.begin = nurroboter
        # self.space.add(tor_balken_1)
        # self.space.add(tor_balken_2)

    def isGoal(self):
        return self.isgoal
