import pygame
from gameconfig import gc
import numpy as np

class Debugger:
    def __init__(self, display, robots):
        self._display = display
        self._robots = robots
        self._id = 0
        self.ppcm = self._display.get_height() / gc.OUTER_FIELD_WIDTH
        self.font = pygame.font.SysFont('Calibri', 20, True, False)
        self.polygonlist = [[3,5],[5,3],[3,1],[3,-1],[5,-3],[3,-5],[-3,-5],[-5,-3],[-5,3],[-3,5]]

    def setFocusedRobot(self, id):
        self._id = id

    def draw(self):
        RED = 255, 0, 0
        BLACK = 0, 0, 0
        BLUE = 0, 0, 255

        # ROBOT
        pos = int((gc.OUTER_FIELD_LENGTH+gc.OUTER_FIELD_WIDTH/2) * self.ppcm), \
              int(gc.OUTER_FIELD_WIDTH/2* self.ppcm)
        newpolygon = []
        scale = 15 * self.ppcm
        for p in self.polygonlist:
            newpolygon.append([(scale*p[0])+pos[0], (scale*p[1])+pos[1]])
        if self._id == 0 or self._id == 1:
            pygame.draw.polygon(self._display, BLUE , newpolygon, 0)
        else:
            pygame.draw.polygon(self._display, RED , newpolygon, 0)



        # ID
        tmp = (pos[0] - 20, pos[1] - 250)
        state = self._robots[self._id].getRobotState()
        text = self.font.render("id: "+str(self._id+1) + " state: " + str(state), True, BLACK)
        self._display.blit(text, tmp)

        # Motors
        motors = self._robots[self._id].motor*100
        tmp = (pos[0] + 120-20, pos[1] + 120)
        text = self.font.render("m0: "+str(int(motors[0])), True, BLACK)
        self._display.blit(text, tmp)
        tmp = (pos[0] - 120-30, pos[1] + 120)
        text = self.font.render("m1: "+str(int(motors[1])), True, BLACK)
        self._display.blit(text, tmp)
        tmp = (pos[0] - 120-30, pos[1] - 120)
        text = self.font.render("m2: "+str(int(motors[2])), True, BLACK)
        self._display.blit(text, tmp)
        tmp = (pos[0] + 120-20, pos[1] - 120)
        text = self.font.render("m3: "+str(int(motors[3])), True, BLACK)
        self._display.blit(text, tmp)

        #Boden Sensors
        boden = self._robots[self._id].getBodenSensors()
        for i in range(0,16):
            winkel = np.deg2rad(i*360/16)
            tmp = (pos[0]+np.cos(winkel)*100-20, pos[1]+np.sin(winkel)*100)
            text = self.font.render(str(i)+": "+str(int(boden[i])), True, BLACK)
            self._display.blit(text, tmp)

        #Ball Sensors
        ball = self._robots[self._id].getIRBall()
        for i in range(0,16):
            winkel = np.deg2rad(i*360/16)
            tmp = (pos[0]+np.cos(winkel)*200-20, pos[1]+np.sin(winkel)*200)
            text = self.font.render(str(i)+": "+str(int(ball[i])), True, BLACK)
            self._display.blit(text, tmp)

        #Kompass
        kompass = self._robots[self._id].getKompass()
        tmp = (pos[0] -40, pos[1] )
        text = self.font.render("cmp: " + str(int(kompass)), True, BLACK)
        self._display.blit(text, tmp)

        #ultraschall
        US = self._robots[self._id].getUltraschall()
        for i in range(0,4):
            winkel = np.deg2rad(i*360/4)
            tmp = (pos[0]+np.cos(winkel)*200-30, pos[1]+np.sin(winkel)*160+20)
            text = self.font.render("US"+str(i)+": "+str(int(US[i])), True, BLACK)
            self._display.blit(text, tmp)

        #LightBarrier
        lb = self._robots[self._id].getLightBarrier()
        if lb == True:
            text = self.font.render("BALL", True, BLACK)
            self._display.blit(text, (20,20))