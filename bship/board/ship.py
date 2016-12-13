import tile as bt

class Ship():
	O_HORIZONTAL = 0
	O_VERTICAL = 1

	FLEET = {
			0: (5, "Carrier"),
			1: (4, "Battleship"),
			2: (3, "Cruiser"),
			3: (3, "Submarine"),
			4: (2, "Destroyer")
			}

	def __init__(self, index):
		self.index = index

		if index in Ship.FLEET:
			self.size = Ship.FLEET[index][0]
			self.name = Ship.FLEET[index][1]
		else:
			self.size = 0
			self.name = ""

		self.pos = (0, 0)
		self.orientation = Ship.O_HORIZONTAL

	def place(self, x, y, orientation):
		self.pos = (x, y)
		self.orientation = orientation

	def is_valid(self):
		if self.index not in Ship.FLEET:
			return False
		return True

	def rect(self):
		if not self.is_valid():
			return None

		if self.orientation == Ship.O_HORIZONTAL:
			return (self.pos[0] * bt.Tile.SIZE, self.pos[1] * bt.Tile.SIZE, 
					self.size * bt.Tile.SIZE, bt.Tile.SIZE)
		return (self.pos[0] * bt.Tile.SIZE, self.pos[1] * bt.Tile.SIZE, 
				bt.Tile.SIZE, self.size * bt.Tile.SIZE)
	
	def tile(self):
		if not self.is_valid():
			return bt.Tile(bt.Tile.T_WATER)
		return bt.Tile(chr(ord('A') + self.index))
