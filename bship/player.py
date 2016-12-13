import board.ship as bs

class Player():
	def __init__(self):
		self.name = "Anon"
		self.score = 0
		self.placing_ships = False
		self.cur_ship_index = 0
		self.cur_ship = None
	
	def set_name(self, name):
		self.name = name
	
	def start_placing_ships(self):
		self.placing_ships = True
		self.cur_ship = bs.Ship(self.cur_ship_index)

	def is_placing_ships(self):
		return self.placing_ships

	def next_ship(self):
		self.cur_ship_index += 1
		index = self.cur_ship_index
		self.cur_ship = bs.Ship(index)

		if self.cur_ship.is_valid():
			return self.cur_ship
		self.placing_ships = False
		return None

	def current_ship(self):
		return self.cur_ship
