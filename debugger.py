import pygame
from gameconfig import gc
import numpy as np

# This is an optional visualisation of the sensor values of an specific robot.
# It can be disabled via the config.yml Gui->Debugger->False



class Debugger:
    def __init__(self, display, robots):
        self._display = display
        self._robots = robots
        self._id = 0

        self.field_width = self._display.get_height();
        self.field_height = self._display.get_width()-self._display.get_height();
        self.ppcm = self._display.get_height() / self.field_width
        self.font = pygame.font.SysFont('Calibri', 20, True, False)
        self.polygonList = [[3,5],[5,3],[3,1],[3,-1],[5,-3],[3,-5],[-3,-5],[-5,-3],[-5,3],[-3,5]]
        self._pixyModeFlag = False

    def setFocusedRobot(self, id):
        self._id = id

    def togglePixyMode(self):
        self._pixyModeFlag = not self._pixyModeFlag

    def draw(self):
        RED = 255, 0, 0
        BLACK = 0, 0, 0
        BLUE = 0, 0, 255

        pos = int((self.field_height + self.field_width / 2) * self.ppcm), \
              int(self.field_width / 2 * self.ppcm)

        # ID
        tmp = (pos[0] - 20, pos[1] - 250)
        state = self._robots[self._id].getRobotState()
        text = self.font.render("id: " + str(self._id + 1) + " state: " + str(state), True, BLACK)
        self._display.blit(text, tmp)


        if self._pixyModeFlag:
            blocks = self._robots[self._id].getPixy()
            #Resolution is 320x200
            topleft = [int(pos[0]+100-320),int(pos[1]+100-200)]
            Rect = [topleft[0],topleft[1],320,200]
            pygame.draw.rect(self._display,BLACK,Rect,1)
            for block in blocks:
                point = [int(topleft[0]+block["y"]),int(topleft[1]+block["x"])]
                if block["signature"] == 1:
                    pygame.draw.circle(self._display, RED, point , int(10 * self.ppcm))
                elif block["signature"] == 2:
                    pygame.draw.rect(self._display, BLACK, [point[0]-5,point[1]-5,10,10])
                elif block["signature"] == 3:
                    pygame.draw.rect(self._display, BLACK,[point[0]-5,point[1]-5,10,10])
            return


        # ROBOT
        pos = int((self.field_height+self.field_width/2) * self.ppcm), \
              int(self.field_width/2* self.ppcm)
        newpolygon = []
        scale = 15 * self.ppcm
        for p in self.polygonList:
            newpolygon.append([(scale*p[0])+pos[0], (scale*p[1])+pos[1]])
        if self._id == 0 or self._id == 1:
            pygame.draw.polygon(self._display, BLUE , newpolygon, 0)
        else:
            pygame.draw.polygon(self._display, RED , newpolygon, 0)





        # Motors
        motors = self._robots[self._id]._motors*100
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
        if lb:
            text = self.font.render("BALL", True, BLACK)
            self._display.blit(text, (20,20))