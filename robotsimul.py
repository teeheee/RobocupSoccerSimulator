#!/usr/bin/env python2


import pygame
from pygame.locals import *
from grafik import *
from game import *
import time


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 243*3,182*3

    def on_init(self):
		pygame.init()
		self._display_surf = pygame.display.set_mode(self.size, pygame.DOUBLEBUF)
		self._running = True
		self.field = FeldGrafik(self._display_surf)
		self.ball = BallGrafik(self._display_surf)
		self.robot1 = RobotGrafik(self._display_surf,1)
		self.robot2 = RobotGrafik(self._display_surf,2)
		self.robot3 = RobotGrafik(self._display_surf,3)
		self.robot4 = RobotGrafik(self._display_surf,4)
		self.robot1.moveto(13,1,0)
		self.robot2.moveto(80,-1,0)
		self.robot3.moveto(-40,2,0)
		self.robot4.moveto(-80,3,0)

		robots = (Robot(self.robot1),Robot(self.robot2),Robot(self.robot3),Robot(self.robot4))
		ball = Ball(self.ball)
		self.game = Game(ball,robots)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.game.tick(1)
        time.sleep(0.01)
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.game.ris[0].robot.motor = np.array([1,0,-1,0])
        if keys[K_RIGHT]:
            self.game.ris[0].robot.motor = np.array([-1,0,1,0])
        if keys[K_UP]:
            self.game.ris[0].robot.motor = np.array([0,1,0,-1])
        if keys[K_DOWN]:
            self.game.ris[0].robot.motor = np.array([0,-1,0,1])

    def on_render(self):
		self.field.draw()
		self.robot1.draw()
		self.robot2.draw()
		self.robot3.draw()
		self.robot4.draw()
		self.ball.draw()
		pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
