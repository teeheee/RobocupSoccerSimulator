import pygame
#from pygame.locals import *
import numpy as np
from gameconfig import gc

WHITE = 255, 255, 255
GREEN = 0, 255, 0
BLACK = 0, 0, 0
GREY = 100, 100, 100
BLUE = 0, 0, 255
RED = 255, 0, 0
YELLOW = 255, 255, 0
ORANGE = 255, 69, 0
BROWN = 139, 69, 19


class BallGraphic:
    # display: the pygame display to draw to
    def __init__(self, game_display_data):
        self._display = game_display_data["display"]
        self._ppcm = game_display_data["ppcm"]
        self._y_position_offset = game_display_data["center"][0]
        self._x_position_offset = game_display_data["center"][1]
        self._y_position = 0
        self._x_position = 0

    # draw ball graphic to display
    def draw(self):
        pos = (int((self._x_position + self._x_position_offset) * self._ppcm),
               int((self._y_position + self._y_position_offset) * self._ppcm))
        pygame.draw.circle(self._display, ORANGE, pos, int(3 * self._ppcm))

    # move ball to x, y in cm
    def moveto(self, x, y):
        self._x_position = x
        self._y_position = y


class RobotGraphic:
    # display: the pygame display to draw to
    # id: the robot id which is drawn on the back of the robot
    # color: color of the robot
    # direction: orientation of the text on the robot (to make it more readable)
    def __init__(self, game_display_data, id, color, direction):
        self._display = game_display_data["display"]
        self._ppcm = game_display_data["ppcm"]
        self._y_position_offset = game_display_data["center"][0]
        self._x_position_offset = game_display_data["center"][1]
        self._direction = direction
        self._color = color
        self._y_position = 0
        self._x_position = 0
        self._orientation = 0
        self._id = id
        self._font = pygame.font.SysFont('Calibri', 20, True, False)
        self._polygonlist = [[3,5],[5,3],[3,1],[3,-1],[5,-3],[3,-5],[-3,-5],[-5,-3],[-5,3],[-3,5]]

    # draw robot graphic to display
    def draw(self):
        pos = int((self._x_position + self._x_position_offset) * self._ppcm), \
              int((self._y_position + self._y_position_offset) * self._ppcm)
        newpolygon = []
        a = np.deg2rad(self._orientation)
        scale = 10 / 5.83 * self._ppcm
        for p in self._polygonlist:
            x = p[0]
            y = p[1]
            newpolygon.append([(x*np.cos(a)+y*np.sin(a)) * scale + pos[0] ,(y*np.cos(a)-x*np.sin(a)) * scale + pos[1] ])
        pygame.draw.polygon(self._display, self._color, newpolygon, 0)
        pos = (pos[0] - 5, pos[1] - 8)
        text = self._font.render(str(self._id), True, WHITE)
        text = pygame.transform.rotate(text, self._orientation+self._direction)
        self._display.blit(text, pos)


    # move robot to x and y in cm and orientation in degree
    def moveto(self, x, y, orientation):
        self._x_position = x
        self._y_position = y
        self._orientation = orientation

class DebugOutput:
    # display: the pygame display to draw to
    def __init__(self, game_display_data):
        self._display = game_display_data["display"]
        self._ppcm = game_display_data["ppcm"]
        self._y_position_offset = game_display_data["center"][0]
        self._x_position_offset = game_display_data["center"][1]
        self.ellipseActiveFlag = False
        self.ellipseX = 0
        self.ellipseY = 0
        self.ellipsePX = 0
        self.ellipsePY = 0

    def drawEllipse(self,x,y,px,py):
        self.ellipseX = x
        self.ellipseY = y
        self.ellipsePX = px
        self.ellipsePY = py
        self.ellipseActiveFlag = True

    def draw(self):
        if self.ellipseActiveFlag:
            rect = pygame.Rect((self.ellipseX-self.ellipsePX/2 + self._display.center[0])*self._ppcm,
                               (self.ellipseY-self.ellipsePY/2 + self._display.center[1])*self._ppcm,
                               self.ellipsePX*self._ppcm,
                               self.ellipsePY*self._ppcm )
            try:
                pygame.draw.ellipse(self._display,GREY,rect,2)
            except:
                pass


class FieldGraphic:
    # display: the pygame display to draw to
    def __init__(self, game_display_data):
        self._display = game_display_data["display"]
        self._ppcm = game_display_data["ppcm"]
        self._y_position_offset = game_display_data["center"][0]
        self._x_position_offset = game_display_data["center"][1]
        self._outer_size = (gc.FIELD["BorderLength"],
                            gc.FIELD["BorderWidth"])
        self._inner_size = (gc.FIELD["TouchlineLength"],
                            gc.FIELD["TouchlineWidth"])
        self._goal_size = (gc.FIELD["GoalDepth"], gc.FIELD["GoalWidth"])
        self._linewidth = 1
        self._font = pygame.font.SysFont('Calibri', 20, True, False)
        self._background_display = pygame.Surface((self._display.get_width() , self._display.get_height() ))
        self._drawInit()
        self._score = (0, 0)
        self._time = 0

    def _drawInit(self):
        self._background_display.fill(GREEN)

        offset = (self._x_position_offset - self._inner_size[0] / 2,
                  self._y_position_offset - self._inner_size[1] / 2 )

        # Strafraeume
        r1 = pygame.Rect(
            (offset[0] * self._ppcm,
            (offset[1]+15) * self._ppcm, 30 * self._ppcm, 90 * self._ppcm))
        r2 = pygame.Rect(
            (offset[0] + self._inner_size[0] - 30) * self._ppcm,
            (offset[1]+15) * self._ppcm, 30 * self._ppcm, 90 * self._ppcm)
        pygame.draw.rect(self._background_display, BLACK, r1, int(self._linewidth * self._ppcm * 0.8))
        pygame.draw.rect(self._background_display, BLACK, r2, int(self._linewidth * self._ppcm * 0.8))

        # Auslinien

        if gc.FIELD["TouchlineActive"]:
            ausColor = WHITE
        else:
            ausColor = BROWN
        p1 = (offset[0] * self._ppcm, offset[1] * self._ppcm)
        p2 = (p1[0], p1[1] + self._inner_size[1] * self._ppcm)
        p3 = (p2[0] + self._inner_size[0] * self._ppcm, p2[1])
        p4 = (p3[0], p3[1] - self._inner_size[1] * self._ppcm)
        pygame.draw.line(self._background_display, ausColor, p1, p2, int(self._linewidth * self._ppcm))
        pygame.draw.line(self._background_display, ausColor, p2, p3, int(self._linewidth * self._ppcm))
        pygame.draw.line(self._background_display, ausColor, p3, p4, int(self._linewidth * self._ppcm))
        pygame.draw.line(self._background_display, ausColor, p4, p1, int(self._linewidth * self._ppcm))

        # Tore
        r1 = pygame.Rect(
            (self._x_position_offset - self._goal_size[0] - gc.FIELD["TouchlineLength"]/2) * self._ppcm,
            (self._y_position_offset - self._goal_size[1] / 2) * self._ppcm,
            self._goal_size[0] * self._ppcm,
            self._goal_size[1] * self._ppcm)
        r2 = pygame.Rect(
            (self._x_position_offset  + gc.FIELD["TouchlineLength"] / 2) * self._ppcm,
            (self._y_position_offset - self._goal_size[1] / 2) * self._ppcm,
            self._goal_size[0] * self._ppcm,
            self._goal_size[1] * self._ppcm)
        pygame.draw.rect(self._background_display, BLUE, r1)
        pygame.draw.rect(self._background_display, YELLOW, r2)

        # Mittelkreis
        p1 = (int(self._x_position_offset * self._ppcm), int(self._y_position_offset * self._ppcm))
        pygame.draw.circle(self._background_display, BLACK, p1, int(30 * self._ppcm), 1)

        # Neutrale Punkte
        neutral_x_offset = self._inner_size[0]/2 - 45
        p1 = \
            int((self._x_position_offset - neutral_x_offset) * self._ppcm), \
            int((self._y_position_offset - self._goal_size[1] / 2) * self._ppcm)
        p2 = \
            int((self._x_position_offset + neutral_x_offset) * self._ppcm), \
            int((self._y_position_offset - self._goal_size[1] / 2) * self._ppcm)
        p3 = \
            int((self._x_position_offset - neutral_x_offset) * self._ppcm), \
                int((self._y_position_offset + self._goal_size[1] / 2) * self._ppcm)
        p4 = \
            int((self._x_position_offset + neutral_x_offset) * self._ppcm), \
                int((self._y_position_offset + self._goal_size[1] / 2) * self._ppcm)
        p5 = int(self._x_position_offset * self._ppcm), int(self._y_position_offset * self._ppcm)

        pygame.draw.circle(self._background_display, BLACK, p1, int(1 * self._ppcm))
        pygame.draw.circle(self._background_display, BLACK, p2, int(1 * self._ppcm))
        pygame.draw.circle(self._background_display, BLACK, p3, int(1 * self._ppcm))
        pygame.draw.circle(self._background_display, BLACK, p4, int(1 * self._ppcm))
        pygame.draw.circle(self._background_display, BLACK, p5, int(1 * self._ppcm))

    # draw the field with score and time
    def draw(self):
        # Draw static image
        self._display.blit(self._background_display, (0, 0))
        # Draw Score
        text = self._font.render(str(self._score[0]) + " " + str(self._score[1]), True, BLUE)
        self._display.blit(text, (self._display.get_width() / 2, 10))
        #Draw time in seconds
        text = self._font.render(str(self._time) + " s", True, BLUE)
        self._display.blit(text, (self._display.get_width() / 2, 25))

    # display the current game score
    def setScore(self, a, b):
        self._score = (a, b)

    # display the current time
    def setTime(self, time):
        self._time = time
