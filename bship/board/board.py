import tile as bt
import ship as bs
import pygame

class GameBoard():
	"""
	A game board class.
	Basically it's the waters that will have ships in it.
	"""

	def __init__(self, w = 10, h = 10):
		self.w = w
		self.h = h
		self.our_tiles = [[bt.Tile(bt.Tile.T_WATER)]*w]*h
		self.their_tiles = [[bt.Tile()]*w]*h
		self.ships = []

	def dump(self):
		"""
		Print the gameboard.
		"""
		print("Our waters:")
		for y in range(self.h):
			for x in range(self.w):
				print(self.our_tiles[x][y]),
			print("")
		print("Foreign waters:")
		for y in range(self.h):
			for x in range(self.w):
				print(self.their_tiles[x][y]),
			print("")
	
	def get_our_tile(self, x, y):
		return self.our_tiles[x][y]

	def set_our_tile(self, x, y, value):
		self.our_tiles[x][y] = value
	
	def place_ship(self, ship_id, x, y, orientation):
		"""
		Place a ship on the gameboard.
		"""
		dx = (orientation == GameBoard.O_HORIZONTAL)
		dy = (orientation == GameBoard.O_VERTICAL)
		# Check if there's enough space first.
		for i in range(size):
			tile = self.get_our_tile(x + i * dx, y + i * dy)
			if tile.is_free():
				raise ValueError("You already have a ship there!")

		# Enlist the ship in the navy.
		ship = bs.Ship(ship_id)
		ship.place(x, y, orientation)
		self.ships.append(ship)
		# Mark the tiles occupied by the ship.
		for i in range(size):
			self.set_our_tile(x + i * dx, y + i * dy, ship.tile())

	def render_grid(self, surface, color, pos, size):
		"""
		Render a gameboard grid with the specified
		position, size, and color.
		"""
		ax, ay = pos
		sx, sy = size
		bx = ax + sx
		by = ay + sy

		tsx = sx / self.w
		tsy = sy / self.h

		# Draw vertical lines.
		for x in range(ax, bx, tsx):
			pygame.draw.aaline(
					surface, color, 
					(x, ay), (x, by), 1)
		# Draw horizontal lines.
		for y in range(ay, by, tsy):
			pygame.draw.aaline(
					surface, color, 
					(ax, y), (bx, y), 1)
		# Draw a rect around it.
		pygame.draw.rect(surface, color, (ax, ay, sx, sy), 1)

	def render_tiles(self, surface, tiles, pos):
		# TODO:: Make it scalable.

		tsize = bt.Tile.SIZE

		# Render tiles.
		for y in range(self.h):
			for x in range(self.w):
				tile = tiles[x][y]
				tile.render(surface, 
						(pos[0] + x * tsize, 
							pos[1] + y * tsize))
		# Render the grid on top.
		color = (0, 51, 102, 0)
		self.render_grid(
				surface, color, 
				pos, (self.w * tsize, self.h * tsize))

	def render(self):
		"""
		Render the gameboard, which consists
		of two grids (ours, theirs).
		"""

		# TODO:: Make it scalable.

		tsize = bt.Tile.SIZE

		# Create a surface to render to
		# (the size of the board).
		surface = pygame.Surface(
				(2 * (self.w + 1) * tsize, self.h * tsize))

		self.render_tiles(surface, 
				self.our_tiles, 
				(0, 0))

		self.render_tiles(surface,
				self.their_tiles,
				((self.w + 1) * tsize, 0))

		return surface
