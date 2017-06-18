import pygame
from pygame.locals import *
import gameconfig

WHITE = 255,255,255
GREEN = 0,255,0
BLACK = 0,0,0
GREY = 100,100,100
BLUE = 0,0,255
RED = 255,0,0
YELLOW = 255,255,0
ORANGE = 255,69,0


class BallGrafik:
	def __init__(self,_display):
		self.display = _display
		self.ppcm = self.display.get_height()/gameconfig.OUTER_FIELD_WIDTH
		self.y_position_offset = self.display.get_height()/(2*self.ppcm)
		self.x_position_offset = self.display.get_width()/(2*self.ppcm)
		self.y_position = 0
		self.x_position = 0

	def draw(self):
		pos = int((self.x_position+self.x_position_offset)*self.ppcm), int((self.y_position+self.y_position_offset)*self.ppcm)
		pygame.draw.circle(self.display,ORANGE,pos,3*self.ppcm)

	def moveto(self,x,y):
		self.x_position = x
		self.y_position = y


class RobotGrafik:
	def __init__(self,_display,_id,_color):
		self.display = _display
		self.color = _color
		self.ppcm = self.display.get_height()/gameconfig.OUTER_FIELD_WIDTH
		self.y_position_offset = self.display.get_height()/(2*self.ppcm)
		self.x_position_offset = self.display.get_width()/(2*self.ppcm)
		self.y_position = 0
		self.x_position = 0
		self.orientation = 0
		self.id = _id
		self.font = pygame.font.SysFont('Calibri', 20, True, False)

	def draw(self):
		pos = int((self.x_position+self.x_position_offset)*self.ppcm), int((self.y_position+self.y_position_offset)*self.ppcm)
		pygame.draw.circle(self.display,self.color,pos,10*self.ppcm)
		pos = pos[0]-5 , pos[1]-8
		text = self.font.render(str(self.id), True, WHITE)
		text = pygame.transform.rotate(text, self.orientation)
		self.display.blit(text,pos)

	def moveto(self,x,y,d):
		self.x_position = x
		self.y_position = y
		self.orientation = d


class FeldGrafik:
	def __init__(self,_display):
		self.display = _display
		self.outer_size = (gameconfig.OUTER_FIELD_LENGTH,gameconfig.OUTER_FIELD_WIDTH)
		self.inner_size = (gameconfig.INNER_FIELD_LENGTH,gameconfig.INNER_FIELD_WIDTH)
		self.goal_size = (gameconfig.GOAL_DEEP,gameconfig.GOAL_WIDTH)
		self.linewidth = 1
		self.ppcm = self.display.get_height()/self.outer_size[1]
		self.spielStand = (0,0)
		self.font = pygame.font.SysFont('Calibri', 20, True, False)

	def draw(self):
		self.display.fill(GREEN)

		#Strafraeume
		r1 = Rect(((self.outer_size[0]-self.inner_size[0])/2)*self.ppcm , ((self.outer_size[1]-90)/2)*self.ppcm , 30*self.ppcm,90*self.ppcm)
		r2 = Rect(((self.outer_size[0]-self.inner_size[0])/2+self.inner_size[0]-30)*self.ppcm , ((self.outer_size[1]-90)/2)*self.ppcm , 30*self.ppcm,90*self.ppcm)
		pygame.draw.rect(self.display,BLACK,r1,self.linewidth*self.ppcm)
		pygame.draw.rect(self.display,BLACK,r2,self.linewidth*self.ppcm)

		#Auslinien
		p1 = (((self.outer_size[0]-self.inner_size[0])/2)*self.ppcm, ((self.outer_size[1]-self.inner_size[1])/2)*self.ppcm)
		p2 = (p1[0] , p1[1]+self.inner_size[1]*self.ppcm)
		p3 = (p2[0]+self.inner_size[0]*self.ppcm , p2[1])
		p4 = (p3[0] , p3[1]-self.inner_size[1]*self.ppcm)
		pygame.draw.line(self.display, WHITE, p1, p2, self.linewidth*self.ppcm)
		pygame.draw.line(self.display,WHITE,p2,p3,self.linewidth*self.ppcm)
		pygame.draw.line(self.display,WHITE,p3,p4,self.linewidth*self.ppcm)
		pygame.draw.line(self.display,WHITE,p4,p1,self.linewidth*self.ppcm)

		#Tore
		r1 = Rect(((self.outer_size[0]-self.inner_size[0])/2-self.goal_size[0])*self.ppcm , ((self.outer_size[1]-self.goal_size[1])/2)*self.ppcm , self.goal_size[0]*self.ppcm,self.goal_size[1]*self.ppcm)
		r2 = Rect(((self.outer_size[0]-self.inner_size[0])/2+self.inner_size[0])*self.ppcm , ((self.outer_size[1]-self.goal_size[1])/2)*self.ppcm , self.goal_size[0]*self.ppcm,self.goal_size[1]*self.ppcm)
		pygame.draw.rect(self.display,BLUE,r1)
		pygame.draw.rect(self.display,YELLOW,r2)

		#Mittelkreis
		p1 = self.outer_size[0]/2*self.ppcm ,  self.outer_size[1]/2*self.ppcm
		pygame.draw.circle(self.display,BLACK,p1,30*self.ppcm,1)

		#Neutrale Punkte
		p1 = ((self.outer_size[0]-self.inner_size[0])/2+45)*self.ppcm , ((self.outer_size[1]-self.goal_size[1])/2)*self.ppcm
		p2 = ((self.outer_size[0]-self.inner_size[0])/2+self.inner_size[0]-45)*self.ppcm , ((self.outer_size[1]-self.goal_size[1])/2)*self.ppcm
		p3 = ((self.outer_size[0]-self.inner_size[0])/2+45)*self.ppcm , ((self.outer_size[1]+self.goal_size[1])/2)*self.ppcm
		p4 = ((self.outer_size[0]-self.inner_size[0])/2+self.inner_size[0]-45)*self.ppcm , ((self.outer_size[1]+self.goal_size[1])/2)*self.ppcm
		p5 = self.outer_size[0]/2*self.ppcm,  self.outer_size[1]/2*self.ppcm

		pygame.draw.circle(self.display,BLACK,p1,1*self.ppcm)
		pygame.draw.circle(self.display,BLACK,p2,1*self.ppcm)
		pygame.draw.circle(self.display,BLACK,p3,1*self.ppcm)
		pygame.draw.circle(self.display,BLACK,p4,1*self.ppcm)
		pygame.draw.circle(self.display,BLACK,p5,1*self.ppcm)

		text = self.font.render(str(self.spielStand[0])+" "+str(self.spielStand[1]), True, RED)
		self.display.blit(text,(self.display.get_width()/2,10))

	def setSpielstand(self, a, b):
		self.spielStand = (a,b)
