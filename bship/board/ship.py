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
		self.size = Ship.FLEET[index][0]
		self.name = Ship.FLEET[index][1]

	def place(self, x, y, orientation):
		self.pos = (x, y)
		self.orientation = orientation
	
	def tile(self):
		return bt.Tile('A' + self.index)
