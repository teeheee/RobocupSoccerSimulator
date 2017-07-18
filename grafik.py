import pygame
from pygame.locals import *
import gameconfig
import numpy as np

WHITE = 255, 255, 255
GREEN = 0, 255, 0
BLACK = 0, 0, 0
GREY = 100, 100, 100
BLUE = 0, 0, 255
RED = 255, 0, 0
YELLOW = 255, 255, 0
ORANGE = 255, 69, 0

#TODO more comments

class BallGrafik:
    def __init__(self, _display):
        self.display = _display
        self.ppcm = self.display.get_height() / gameconfig.OUTER_FIELD_WIDTH
        self.y_position_offset = self.display.get_height() / (2 * self.ppcm)
        self.x_position_offset = self.display.get_width() / (2 * self.ppcm)
        self.y_position = 0
        self.x_position = 0

    def draw(self):
        pos = (int((self.x_position + self.x_position_offset) * self.ppcm),
               int((self.y_position + self.y_position_offset) * self.ppcm))
        pygame.draw.circle(self.display, ORANGE, pos, int(3 * self.ppcm))

    def moveto(self, x, y):
        self.x_position = x
        self.y_position = y


class RobotGrafik:
    def __init__(self, _display, _id, _color, _direction):
        self.display = _display
        self.direction = _direction
        self.color = _color
        self.ppcm = self.display.get_height() / gameconfig.OUTER_FIELD_WIDTH
        self.y_position_offset = self.display.get_height() / (2 * self.ppcm)
        self.x_position_offset = self.display.get_width() / (2 * self.ppcm)
        self.y_position = 0
        self.x_position = 0
        self.orientation = 0
        self.id = _id
        self.font = pygame.font.SysFont('Calibri', 20, True, False)
        self.polygonlist = [[3,5],[5,3],[3,1],[3,-1],[5,-3],[3,-5],[-3,-5],[-5,-3],[-5,3],[-3,5]]



    def draw(self):
        pos = int((self.x_position + self.x_position_offset) * self.ppcm), \
              int((self.y_position + self.y_position_offset) * self.ppcm)
        newpolygon = []
        a = np.deg2rad(self.orientation)
        scale = 10 / 5.83 * self.ppcm
        for p in self.polygonlist:
            x = p[0]
            y = p[1]
            newpolygon.append([(x*np.cos(a)+y*np.sin(a)) * scale + pos[0] ,(y*np.cos(a)-x*np.sin(a)) * scale + pos[1] ])
        pygame.draw.polygon(self.display, self.color, newpolygon, 0)
        pos = (pos[0] - 5, pos[1] - 8)
        text = self.font.render(str(self.id), True, WHITE)
        text = pygame.transform.rotate(text, self.orientation+self.direction)
        self.display.blit(text, pos)

    def moveto(self, x, y, d):
        self.x_position = x
        self.y_position = y
        self.orientation = d


class FeldGrafik: #TODO linien nicht korrekt
    def __init__(self, _display):
        self.display = _display
        self.outer_size = (gameconfig.OUTER_FIELD_LENGTH,
                           gameconfig.OUTER_FIELD_WIDTH)
        self.inner_size = (gameconfig.INNER_FIELD_LENGTH,
                           gameconfig.INNER_FIELD_WIDTH)
        self.goal_size = (gameconfig.GOAL_DEEP, gameconfig.GOAL_WIDTH)
        self.linewidth = 1
        self.ppcm = self.display.get_height() / self.outer_size[1]
        self.spielStand = (0, 0)
        self.font = pygame.font.SysFont('Calibri', 20, True, False)
        self.background_display = pygame.Surface((self.display.get_width() , self.display.get_height() ))
        self.drawInit()

    def drawInit(self):
        self.background_display.fill(GREEN)

        # Strafraeume
        r1 = Rect(
            ((self.outer_size[0] - self.inner_size[0]) / 2) * self.ppcm,
            ((self.outer_size[1] - 90) / 2) * self.ppcm, 30 * self.ppcm, 90 * self.ppcm)
        r2 = Rect(
            ((self.outer_size[0] - self.inner_size[0]) / 2 + self.inner_size[0] - 30) * self.ppcm,
            ((self.outer_size[1] - 90) / 2) * self.ppcm, 30 * self.ppcm, 90 * self.ppcm)
        pygame.draw.rect(self.background_display, BLACK, r1, int(self.linewidth * self.ppcm))
        pygame.draw.rect(self.background_display, BLACK, r2, int(self.linewidth * self.ppcm))

        # Auslinien
        p1 = (((self.outer_size[0] - self.inner_size[0]) / 2) * self.ppcm,
              ((self.outer_size[1] - self.inner_size[1]) / 2) * self.ppcm)
        p2 = (p1[0], p1[1] + self.inner_size[1] * self.ppcm)
        p3 = (p2[0] + self.inner_size[0] * self.ppcm, p2[1])
        p4 = (p3[0], p3[1] - self.inner_size[1] * self.ppcm)
        pygame.draw.line(self.background_display, WHITE, p1, p2, int(self.linewidth * self.ppcm))
        pygame.draw.line(self.background_display, WHITE, p2, p3, int(self.linewidth * self.ppcm))
        pygame.draw.line(self.background_display, WHITE, p3, p4, int(self.linewidth * self.ppcm))
        pygame.draw.line(self.background_display, WHITE, p4, p1, int(self.linewidth * self.ppcm))

        # Tore
        r1 = Rect(
            ((self.outer_size[0] - self.inner_size[0]) / 2 - self.goal_size[0]) * self.ppcm,
            ((self.outer_size[1] - self.goal_size[1]) / 2) * self.ppcm,
            self.goal_size[0] * self.ppcm, self.goal_size[1] * self.ppcm)
        r2 = Rect(
            ((self.outer_size[0] - self.inner_size[0]) / 2 + self.inner_size[0]) * self.ppcm,
            ((self.outer_size[1] - self.goal_size[1]) / 2) * self.ppcm,
            self.goal_size[0] * self.ppcm, self.goal_size[1] * self.ppcm)
        pygame.draw.rect(self.background_display, BLUE, r1)
        pygame.draw.rect(self.background_display, YELLOW, r2)

        # Mittelkreis
        p1 = (int(self.outer_size[0] / 2 * self.ppcm), int(self.outer_size[1] / 2 * self.ppcm))
        pygame.draw.circle(self.background_display, BLACK, p1, int(30 * self.ppcm), 1)

        # Neutrale Punkte
        p1 = \
            int(((self.outer_size[0] - self.inner_size[0]) / 2 + 45) * self.ppcm), \
            int(((self.outer_size[1] - self.goal_size[1]) / 2) * self.ppcm)
        p2 = \
            int(((self.outer_size[0] - self.inner_size[0]) / 2 + self.inner_size[0] - 45) * self.ppcm), \
            int(((self.outer_size[1] - self.goal_size[1]) / 2) * self.ppcm)
        p3 = \
            int(((self.outer_size[0] - self.inner_size[0]) / 2 + 45) * self.ppcm), \
                int(((self.outer_size[1] + self.goal_size[1]) / 2) * self.ppcm)
        p4 = \
            int(((self.outer_size[0] - self.inner_size[0]) / 2 + self.inner_size[0] - 45) * self.ppcm), \
                int(((self.outer_size[1] + self.goal_size[1]) / 2) * self.ppcm)
        p5 = int(self.outer_size[0] / 2 * self.ppcm), int(self.outer_size[1] / 2 * self.ppcm)

        pygame.draw.circle(self.background_display, BLACK, p1, int(1 * self.ppcm))
        pygame.draw.circle(self.background_display, BLACK, p2, int(1 * self.ppcm))
        pygame.draw.circle(self.background_display, BLACK, p3, int(1 * self.ppcm))
        pygame.draw.circle(self.background_display, BLACK, p4, int(1 * self.ppcm))
        pygame.draw.circle(self.background_display, BLACK, p5, int(1 * self.ppcm))


    def draw(self):
        self.display.blit(self.background_display, (0, 0))
        text = self.font.render(str(self.spielStand[0]) + " " + str(self.spielStand[1]), True, BLUE)
        self.display.blit(text, (self.display.get_width() / 2, 10))

    def setSpielstand(self, a, b):
        self.spielStand = (a, b)
