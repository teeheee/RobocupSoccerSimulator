from gameconfig import gc
from interface import *
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
        # For updateing the robot position
        self.robotgrafik = _robotgrafik
        # pymunk space
        self.space = _space
        # radius of the robot in cm
        self.radius = 10
        # mass of the robot in kg
        self.mass = 2000
        # maximum velocity in m/ms TODO check this????
        self.vmax = 0.2
        # maximum torque for all wheels combined in Nm
        self.fmax = 0.5
        # motor speed array
        self.motor = np.array([0, 0, 0, 0])
        # indicator if the robot is "defekt"
        self.defekt = False

        # configure the Body of the Robot
        self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius, (0, 0)))
        self.body.position = ((self.robotgrafik.x_position, self.robotgrafik.y_position))
        self.body.angle = np.radians(self.robotgrafik.orientation)
        self.body.name = "robot" + str(self.robotgrafik.id)

        # generate the special shape of the robot.
        # because the ballcapture zone is not concave two polygons are needed
        polygonlist1 = [[3,5],[5,3],[3,1],[3,-1],[-5,-1],[-5,3],[-3,5]]
        polygonlist2 = [[3,1],[5,-3],[3,-5],[-3,-5],[-5,-3],[-5,1]]

        # scale polygon to correct size
        scale = 10 / 5.83 #scaling 10/5.83 = 10/sqrt(3¹+5¹)
        newpolygon1 = []
        for p in polygonlist1:
            newpolygon1.append([p[0]*scale,p[1]*scale])
        newpolygon2 = []
        for p in polygonlist2:
                newpolygon2.append([p[0] * scale, p[1] * scale])

        # generate Robot shapes
        self.shape1 = pymunk.Poly(self.body, newpolygon1)
        self.shape1.elasticity = 0
        self.shape1.friction = 0.9
        self.shape1.collision_type = collision_types["robot"]
        self.shape2 = pymunk.Poly(self.body, newpolygon2)
        self.shape2.elasticity = 0
        self.shape2.friction = 0.9
        self.shape2.collision_type = collision_types["robot"]

        # add shapes to Body
        self.space.add(self.body, self.shape1 ,self.shape2)

    def motorSpeed(self, a, b, c, d):
        self.motor = np.array([a, b, c, d])

    def moveto(self, x, y, d):
        self.body.position = (x, y)
        self.body.angle = np.radians(d)
        self.space.reindex_shapes_for_body(self.body)

    def tick(self): #TODO there ist still something wrong with this
        if self.defekt:
            self.motor = np.array([0, 0, 0, 0])
            self.body.torque = 0
            self.body.force = (0, 0)
        else:
            self.robotgrafik.moveto((self.body.position.x), (self.body.position.y), -np.degrees(self.body.angle))
            A = np.array([[1, 0, -1, 0], [0, 1, 0, -1], [10, 10, 10, 10]])*self.fmax
            f = A.dot(self.motor)
            theta = self.body.angle - np.deg2rad(45 + 180)
            c, s = np.cos(theta), np.sin(theta)
            R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
            v = np.array([self.body.velocity[0], self.body.velocity[1], self.body.angular_velocity])
            f = R.dot(f)
            f_soll = (f - (self.fmax / self.vmax) * v)
            self.body.torque = f_soll[2]
            self.body.force = tuple(f_soll[0:2])

    def isPushedByRobot(self, robot):
        #every robot has two shapes so 4 collisions need to be checkt between each robot
        p1 = self.shape1.shapes_collide(robot.shape1)
        p2 = self.shape1.shapes_collide(robot.shape2)
        p3 = self.shape2.shapes_collide(robot.shape1)
        p4 = self.shape2.shapes_collide(robot.shape2)
        if len(p1.points) > 0 or len(p2.points) > 0 or len(p3.points) > 0 or len(p4.points) > 0:
            return True
        return False

    def isPushedByBall(self, ball):
        #every robot has two shapes so 2 collisions need to be checkt
        p1 = self.shape1.shapes_collide(ball.shape)
        p2 = self.shape2.shapes_collide(ball.shape)
        if len(p1.points) > 0 or len(p2.points) > 0:
            return True
        return False

    def getUS(self):
        usValue = np.array([0,0,0,0])
        filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0x1) #this is some pymunk voodoo
        queryList = list()
        radians = self.body.angle
        rotationMatrix = np.array([(np.cos(radians),-np.sin(radians)),
                                   (np.sin(radians), np.cos(radians))])
        v1 = np.matmul(rotationMatrix,np.array([200,0]))
        v2 = np.matmul(rotationMatrix,np.array([0,200]))
        v3 = np.matmul(rotationMatrix,np.array([-200,0]))
        v4 = np.matmul(rotationMatrix,np.array([0,-200]))
        queryList.append(self.space.segment_query(self.body.position,self.body.position + v1,5,filter))
        queryList.append(self.space.segment_query(self.body.position,self.body.position + v2,5,filter))
        queryList.append(self.space.segment_query(self.body.position,self.body.position + v3,5,filter))
        queryList.append(self.space.segment_query(self.body.position,self.body.position + v4,5,filter))
        i = 0
        for query in queryList:
            finalReflectionDistance = 200
            for singleQuery in query:
                dotOfInterest = singleQuery.point
                distanceToDotOfInterest = np.linalg.norm(dotOfInterest-self.body.position)
                if distanceToDotOfInterest < finalReflectionDistance:
                    finalReflectionDistance = distanceToDotOfInterest
            usValue[i]=finalReflectionDistance - 10 #subtract radius of robot
            if usValue[i] <= 0:
                usValue[i] = 200
            i = i + 1
        return usValue




class BallPhysik:
    def __init__(self, _space, _ballgrafik):
        self.space = _space
        self.ballgrafik = _ballgrafik

        self.radius = 3
        self.mass = 80
        self.pos = np.array((self.ballgrafik.x_position, self.ballgrafik.y_position))

        self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius, (0, 0)))
        self.body.position = ((self.ballgrafik.x_position, self.ballgrafik.y_position))
        self.body.name = "ball"


        self.shape = pymunk.Circle(self.body, self.radius, (0, 0))
        self.shape.elasticity = 0.95
        self.shape.friction = 10
        self.shape.collision_type = collision_types["ball"]
        self.shape.filter = pymunk.ShapeFilter(categories=0x1)

        self.space.add(self.body, self.shape)

    def moveto(self, x, y):
        self.body.position = (x, y)
        self.body.velocity = (0, 0)
        self.space.reindex_shapes_for_body(self.body)

    def tick(self):
        self.ballgrafik.moveto((self.body.position.x), (self.body.position.y))

    def kick(self,direction):
        theta = np.deg2rad(direction)
        f = (np.cos(theta)*1,np.sin(theta)*1)
        self.body.force = f



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
            linie.filter = pymunk.ShapeFilter(categories=0x1)
            linie.collision_type = collision_types["auslinie"]
            linie.sensor = True

        self.space.add(self.auslinien)

    def tick(self):
        pass

    def getIntersectingPoints(self, robot):
        points = []
        for linie in self.auslinien:
            A = np.array(linie.a)
            B = np.array(linie.b)
            C = np.array(robot.body.position)
            R = 8

            LAB = np.linalg.norm(A-B)
            D = (B - A) / LAB
            t = D * ( C - A )
            E = t * D + A
            LEC = np.linalg.norm(E - C)

            if LEC < R:
                dt = np.sqrt(R-LEC)
                F = (t - dt) * D + A
                G = (t + dt) * D + A
                points.append(F-C)
                points.append(G-C)
            elif LEC == R:
                points.append(E-C)
        return points


class TorPhysik:
    def __init__(self, _space):
        self.isgoal = False
        self.space = _space
        static_body = self.space.static_body
        static_lines_tor1 = [pymunk.Segment(static_body,
                                (gc.INNER_FIELD_LENGTH / 2, gc.GOAL_WIDTH / 2),
                                (gc.INNER_FIELD_LENGTH / 2+gc.GOAL_DEPTH,gc. GOAL_WIDTH/2) ,0.0),
                             pymunk.Segment(static_body,
                                (gc.INNER_FIELD_LENGTH / 2 + gc.GOAL_DEPTH, gc.GOAL_WIDTH / 2),
                                (gc.INNER_FIELD_LENGTH / 2 + gc.GOAL_DEPTH, -gc.GOAL_WIDTH / 2), 0.0),
                             pymunk.Segment(static_body,
                                (gc.INNER_FIELD_LENGTH / 2 + gc.GOAL_DEPTH, -gc.GOAL_WIDTH / 2),
                                (gc.INNER_FIELD_LENGTH / 2, -gc.GOAL_WIDTH / 2), 0.0)]
        static_lines_tor2 = [pymunk.Segment(static_body,
                                (-gc.INNER_FIELD_LENGTH / 2, gc.GOAL_WIDTH / 2),
                                (-gc.INNER_FIELD_LENGTH / 2-gc.GOAL_DEPTH,gc. GOAL_WIDTH/2) ,0.0),
                             pymunk.Segment(static_body,
                                (-gc.INNER_FIELD_LENGTH / 2 - gc.GOAL_DEPTH, gc.GOAL_WIDTH / 2),
                                (-gc.INNER_FIELD_LENGTH / 2 - gc.GOAL_DEPTH, -gc.GOAL_WIDTH / 2), 0.0),
                             pymunk.Segment(static_body,
                                (-gc.INNER_FIELD_LENGTH / 2 - gc.GOAL_DEPTH, -gc.GOAL_WIDTH / 2),
                                (-gc.INNER_FIELD_LENGTH / 2, -gc.GOAL_WIDTH / 2), 0.0)]
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
        def nurball(arbiter, space, data):
            return False

        h1 = self.space.add_collision_handler(collision_types["ball"], collision_types["tor"] )
        h1.begin = nurball

        self.space.add(tor_balken_1)
        self.space.add(tor_balken_2)

    def isGoal(self):
        return self.isgoal


