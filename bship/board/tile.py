import pygame

class Tile():
	SIZE = 32

	T_VOID = ' '
	T_WATER = '~'
	T_OCCUPIED = ':'
	T_BOMBED = '#'

	C_VOID = (0, 0, 0, 0)
	C_WATER = (0, 25, 51, 0)
	C_OCCUPIED = (0, 51, 102, 0)
	C_SHIP = (96, 96, 96, 0)
	C_BOMBED = (102, 0, 0, 0)

	BACKGROUND = {
			' ': C_VOID,
			'~': C_WATER,
			':': C_OCCUPIED,
			'#': C_BOMBED
			}

	def __init__(self, tile=' '):
		self.tile = tile
	
	def __str__(self):
		return self.tile

	def is_free(self):
		return (self.tile == Tile.T_WATER)
	
	def render(self, surface, pos):
		if self.tile in Tile.BACKGROUND:
			color = Tile.BACKGROUND[self.tile]
		else:
			color = Tile.C_SHIP
		rect = (pos[0], pos[1], 
				Tile.SIZE, Tile.SIZE)
		pygame.draw.rect(surface, color, rect, 0)

