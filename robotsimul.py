#!/usr/bin/env python3

from game import *
from debugger import Debugger
from logSaver import Logger
from gameconfig import gc
from popup_menu import *
import sys
import time

#TODO more comments
#TODO clean up this mess

class App:
    def __init__(self):
        # flag for shutdown of the simulation
        self._running = True

        # flags for the keyboard control Interface
        self.robotcontrol = False #True for manual control
        self.pause = False #True for game paused
        self.focusedrobot = 0 #Id of the robot which sensor values are displayed on the debugger

        self._display_surf = None # dubble buffered display to minimize lag
        self.size = self.width, self.height = 243*3, 182*3 # Window size is fixed TODO: variable window size

        self.menu_data = (
            'Robot Simulator',
            'Restart',
            'Quit',
        )
        self.menu = NonBlockingPopupMenu(self.menu_data)

    def on_init(self):
        pygame.init()
        if gc.GUI["Debugger"]:
            width = self.width+self.height
        else:
            width = self.width
        self._display_surf = pygame.display.set_mode((width, self.height), pygame.DOUBLEBUF)
        self._game_display = pygame.Surface( self.size )
        self.ppcm = 3 #TODO: variable window size
        self.center = [self._game_display.get_height() / (2 * self.ppcm),
                                     self._game_display.get_width() / (2 * self.ppcm)]
        self._display_surf.set_alpha(None)
        self._running = True
        game_display_data = {"display": self._game_display,
                             "ppcm": self.ppcm,
                             "center": self.center}
        self.game = Game(game_display_data)

        if gc.GUI["Debugger"]:
            self.debugger = Debugger(self._display_surf, self.game.robotProgramHandlers)
            self.debugger.setFocusedRobot(self.focusedrobot)

        if gc.GUI["Logger"]:
            self.logger = Logger(self.game)
            self.logger.startLogging()

        pygame.mixer.quit()

    def on_event(self, event):
        for e in self.menu.handle_events(event):
            if e.type == USEREVENT:
                if e.code == 'MENU':
                    if e.name is None:
                        self.menu.hide()
                    elif e.text == "Quit":
                        self._running = False
                    elif e.text == "Restart":
                        self.game.restart()
                    else:
                        print('TODO: handle this Menu event: %s' % (e.text)) #TODO menu handling
            elif e.type == MOUSEBUTTONUP:
                self.menu.show()
            elif e.type == pygame.QUIT:
                self._running = False

    def on_loop(self):
        if not self.pause:
            self.logger.tick()
            self.game.tick(30) #calculate in ms steps
        speed = 0.5
        motor = np.array([0.0, 0.0, 0.0, 0.0])
        key = pygame.key.get_pressed()
        if key[pygame.K_UP]:
            motor += np.array([-speed, -speed, speed, speed])
        if key[pygame.K_DOWN]:
            motor += np.array([speed, speed, -speed, -speed])
        if key[pygame.K_RIGHT]:
            motor += np.array([speed/2, 0, speed/2, 0])
        if key[pygame.K_LEFT]:
            motor += np.array([-speed/2, 0, -speed/2, 0])
        if key[pygame.K_m]:
            motor += np.array([-speed, speed, speed, -speed])
        if key[pygame.K_j]:
            motor += np.array([speed, -speed, -speed, speed])
        if key[pygame.K_1]:
            self.focusedrobot = 0
            if gc.GUI["Debugger"]:
                self.debugger.setFocusedRobot(0)
        if key[pygame.K_2]:
            self.focusedrobot = 1
            if gc.GUI["Debugger"]:
                self.debugger.setFocusedRobot(1)
        if key[pygame.K_3]:
            self.focusedrobot = 2
            if gc.GUI["Debugger"]:
                self.debugger.setFocusedRobot(2)
        if key[pygame.K_4]:
            self.focusedrobot = 3
            if gc.GUI["Debugger"]:
                self.debugger.setFocusedRobot(3)
        if key[pygame.K_v]:
            if gc.GUI["Debugger"]:
                self.debugger.togglePixyMode()
        if key[pygame.K_p]:
            self.pause = True
        else:
            self.pause = False
        if key[pygame.K_SPACE]:
            self.robotcontrol=True
        else:
            self.robotcontrol=False

        if self.robotcontrol:
            motor *= 100
            self.game.robotInterfaceHandlers[self.focusedrobot].setMotorSpeed(motor[0], motor[1], motor[2], motor[3])
            self.game.robotProgramHandlers[self.focusedrobot].block()
        else:
            self.game.robotProgramHandlers[self.focusedrobot].unBlock()

    def on_render(self):
        self._display_surf.fill(GREEN)
        self.game.draw()
        self._display_surf.blit(self._game_display,(0, 0))
        if gc.GUI["Debugger"]:
            self.debugger.draw()
        self.menu.draw()
        pygame.display.update()

    def on_cleanup(self):
        self.game.shutdown()
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self._running = False
        while(self._running):

            self.on_event(pygame.event.get())

            self.on_loop()
            if gc.GUI["Fast"] == False:
                time.sleep(0.03)
            self.on_render()

        self.on_cleanup()

if __name__ == "__main__":
    #load config file if it is given as argument
    if len(sys.argv) == 2:
        gc.load(str(sys.argv[1]))
    else:
        gc.load(None)

    theApp = App()
    theApp.on_execute()
