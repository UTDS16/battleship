import logging
import pygame
import tile as bt
import ship as bs

class GameBoard():
	"""
	A game board class.
	Basically it's the waters that will have ships in it.
	"""

	# TODO:: Make a generic module for those
	O_HORIZONTAL = 0
	O_VERTICAL = 1

	def __init__(self, w = 10, h = 10):
		self.log = logging.getLogger("BShip.Board")

		self.w = w
		self.h = h
		# Create a 2D array of our own waters.
		self.our_tiles = [[bt.Tile(bt.Tile.T_WATER) for x in range(w)] for y in range(h)]
		# Create a 2D array of foreign waters.
		self.their_tiles = [[bt.Tile() for x in range(w)] for y in range(h)]
		# List of our ships.
		self.ships = []

		# Cursor parameters.
		self.cur_pos = (0, 0)
		self.cur_orient = GameBoard.O_HORIZONTAL

	def dump(self):
		"""
		Print the gameboard.
		"""
		print("Our waters ... foreign waters:")
		for y in range(self.h):
			for x in range(self.w):
				print(self.our_tiles[x][y]),
			print("\t"),
			for x in range(self.w):
				print(str(self.their_tiles[x][y])),
			print("")
	
	def get_our_tile(self, x, y):
		"""
		Get our tile by coordinates.
		"""
		if x >= 0 and x < self.w and y >= 0 and y < self.h:
			return self.our_tiles[x][y]
		return None

	def set_our_tile(self, x, y, value):
		"""
		Set our tile at specific coordinates.
		"""
		if x >= 0 and x < self.w and y >= 0 and y < self.h:
			self.our_tiles[x][y] = value
	
	def place_ship(self, ship, x, y, orientation):
		"""
		Place a ship on the gameboard.
		"""
		dx = (orientation == GameBoard.O_HORIZONTAL)
		dy = (orientation == GameBoard.O_VERTICAL)
		# Check if there's enough space first.
		for i in range(ship.size):
			tile = self.get_our_tile(x + i * dx, y + i * dy)
			if not tile.is_free():
				raise ValueError("You already have a ship there!")

		self.dump()
		# Enlist the ship in the navy.
		ship.place(x, y, orientation)
		self.ships.append(ship)
		# Mark the tiles occupied by the ship.
		for i in range(ship.size):
			cx = x + i * dx
			cy = y + i * dy

			# Create a tile boundary around the ship.
			tile = bt.Tile(bt.Tile.T_OCCUPIED)
			if i == 0:
				#
				# :AAAAA
				#
				#   :
				#   E
				#   E
				#
				self.set_our_tile(cx - dx, cy - dy, tile)
				# :
				# :AAAAA
				#
				#  ::
				#   E
				#   E
				#
				self.set_our_tile(cx - dx - dy, cy - dy - dx, tile)
				# :
				# :AAAAA
				# :
				#  :::
				#   E
				#   E
				#
				self.set_our_tile(cx - dx + dy, cy - dy + dx, tile)
			elif i == ship.size - 1:
				# :
				# :AAAAA:
				# :
				#  :::
				#   E
				#   E
				#   :
				self.set_our_tile(cx + dx, cy + dy, tile)
				# :     :
				# :AAAAA:
				# :
				#  :::
				#   E
				#   E
				#  ::
				self.set_our_tile(cx + dx - dy, cy + dy - dx, tile)
				# :     :
				# :AAAAA:
				# :     :
				#  :::
				#   E
				#   E
				#  :::
				self.set_our_tile(cx + dx + dy, cy + dy + dx, tile)
			# :::::::
			# :AAAAA:
			# :     :
			#  :::
			#  :E
			#  :E
			#  :::
			self.set_our_tile(cx - dy, cy - dx, tile)
			# :::::::
			# :AAAAA:
			# :::::::
			#  :::
			#  :E:
			#  :E:
			#  :::
			self.set_our_tile(cx + dy, cy + dx, tile)

			# Create the ship tile by tile.
			self.set_our_tile(cx, cy, ship.tile())

		self.dump()
	
	def clicked(self, player, pos):
		"""
		Event handler for gameboard clicks.
		"""
		try:
			print "Clicked"
			if player.is_placing_ships():
				self.place_ship(player.current_ship(), 
						self.cur_pos[0], self.cur_pos[1], self.cur_orient)
				player.next_ship()
		except ValueError as e:
			self.log.exception(e)
			# TODO:: Produce a sound effect and display the error in GUI.

	def rotate_ship(self):
		"""
		Rotate the ship cursor.
		"""
		if self.cur_orient == GameBoard.O_HORIZONTAL:
			self.cur_orient = GameBoard.O_VERTICAL
		else:
			self.cur_orient = GameBoard.O_HORIZONTAL

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
		"""
		Render board tiles.
		"""
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

	def update_cursor(self, player, pos):
		"""
		Update cursor position and the size of the highlight rectangle
		that follows the cursor.
		"""
		tsize = bt.Tile.SIZE
		cpos = (pos[0] / tsize, pos[1] / tsize)

		ship = player.current_ship()

		self.cur_pos = None

		# Horizontal placement?
		if self.cur_orient == bs.Ship.O_HORIZONTAL:
			# Shift mouse to the center of the ship.
			cpos = (cpos[0] - ship.size / 2, cpos[1])
			# Clamp to board edge.
			if cpos[0] < 0:
				cpos = (0, cpos[1])
			elif cpos[0] + ship.size > self.w:
				cpos = (self.w - ship.size, cpos[1])
			# Valid coordinates? Place the ship.
			if cpos[0] >= 0 and cpos[1] >= 0 and cpos[1] < self.h:
				self.cur_pos = cpos
		# Vertical placement?
		elif self.cur_orient == bs.Ship.O_VERTICAL:
			# Shift mouse to the center of the ship.
			cpos = (cpos[0], cpos[1] - ship.size / 2)
			# Clamp to board edge.
			if cpos[1] < 0:
				cpos = (cpos[0], 0)
			elif cpos[1] + ship.size > self.h:
				cpos = (cpos[0], self.h - ship.size)
			# Valid coordinates? Place the ship.
			if cpos[0] >= 0 and cpos[0] < self.w and cpos[1] >= 0:
				self.cur_pos = cpos

	def render_cursor(self, surface, player):
		"""
		Render a highlight rectangle around the imaginary ship to be placed.
		"""
		color = (255, 255, 255, 0)
		ship = player.current_ship()

		if self.cur_pos != None:
			if self.cur_orient == bs.Ship.O_HORIZONTAL:
				ship.place(self.cur_pos[0], self.cur_pos[1], bs.Ship.O_HORIZONTAL)
			elif self.cur_orient == bs.Ship.O_VERTICAL:
				ship.place(self.cur_pos[0], self.cur_pos[1], bs.Ship.O_VERTICAL)

		# In the end, just draw a rectangle.
		pygame.draw.rect(
				surface, color,
				ship.rect(), 1)
	
	def update_crosshair(self, pos):
		tsize = bt.Tile.SIZE
		cpos = (pos[0] / tsize, pos[1] / tsize)

		self.cur_pos = None

		if cpos[0] < self.w + 1:
			cpos = (self.w + 1, cpos[1])
		elif cpos[0] > 2 * self.w:
			cpos = (2 * self.w, cpos[1])
		if cpos[1] < 0:
			cpos = (cpos[0], 0)
		elif cpos[1] > self.h:
			cpos = (cpos[0], self.h - 1)
		self.cur_pos = cpos

	def render_crosshair(self, surface):
		color = (255, 20, 0, 0)

		if self.cur_pos != None:
			rect = (self.cur_pos[0], self.cur_pos[1], bt.Tile.SIZE, bt.Tile.SIZE)
			pygame.draw.rect(
					surface, color,
					rect, 1)


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
