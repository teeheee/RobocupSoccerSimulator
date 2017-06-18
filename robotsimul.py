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
        self._display_surf.set_alpha(None)
        self._running = True
        self.game = Game(self._display_surf)
        pygame.mixer.quit()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.game.tick(0.5)

    def on_render(self):
		self.game.draw()
		pygame.display.update()

    def on_cleanup(self):
        self.game.shutdown()
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self._running = False
        I = 0
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            I=I+1
            if I > 20:
                self.on_render()
                time.sleep(1/30)
                I=0
        self.on_cleanup()

if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
