#!/usr/bin/env python3

from game import *
from debugger import Debugger

#TODO more comments

class App:
    def __init__(self):
        self._running = True
        self.robotcontrol = False
        self.focusedrobot = 0
        self._display_surf = None
        self.size = self.weight, self.height = 243*3, 182*3
        self.pause = False

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.weight+self.height, self.height), pygame.DOUBLEBUF)
        self._game_display = pygame.Surface( self.size )
        self._display_surf.set_alpha(None)
        self._running = True
        self.game = Game(self._game_display)
        self.debugger = Debugger(self._display_surf,self.game.ris)
        self.debugger.setFocusedRobot(2)
        pygame.mixer.quit()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        if not self.pause:
            self.game.tick(0.5)
        speed = 0.5
        motor = np.array([0, 0, 0, 0])
        key = pygame.key.get_pressed()
        if key[pygame.K_UP]:
            motor = motor + np.array([-speed, -speed, speed, speed])
        if key[pygame.K_DOWN]:
            motor = motor + np.array([speed, speed, -speed, -speed])
        if key[pygame.K_RIGHT]:
            motor = motor + np.array([speed/2, 0, speed/2, 0])
        if key[pygame.K_LEFT]:
            motor = motor + np.array([-speed/2, 0, -speed/2, 0])
        if key[pygame.K_m]:
            motor = motor + np.array([-speed, speed, speed, -speed])
        if key[pygame.K_j]:
            motor = motor + np.array([speed, -speed, -speed, speed])
        if key[pygame.K_1]:
            self.focusedrobot = 0
            self.debugger.setFocusedRobot(0)
        if key[pygame.K_2]:
            self.focusedrobot = 1
            self.debugger.setFocusedRobot(1)
        if key[pygame.K_3]:
            self.focusedrobot = 2
            self.debugger.setFocusedRobot(2)
        if key[pygame.K_4]:
            self.focusedrobot = 3
            self.debugger.setFocusedRobot(3)
        if key[pygame.K_p]:
            self.pause = True
        else:
            self.pause = False
        if key[pygame.K_SPACE]:
            self.robotcontrol=True
        else:
            self.robotcontrol=False

        if self.robotcontrol:
            motor = motor*100
            self.game.ris[self.focusedrobot].setMotorSpeed(motor[0], motor[1], motor[2], motor[3])

    def on_render(self):
        self._display_surf.fill(GREEN)
        self.game.draw()
        self._display_surf.blit(self._game_display,(0, 0))
        self.debugger.draw()
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

            I = I + 1
            if I > 80:
                self.on_render()
                I = 0

        self.on_cleanup()

if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
