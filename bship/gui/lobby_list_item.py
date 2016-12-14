import ocempgui.widgets as ow

class LobbyListItem(ow.components.TextListItem):
	"""
	A listbox item with text and UUID.
	"""

	def __init__(self, server):
		self.server = server
		text = str(self)

		ow.components.TextListItem.__init__(self, text)
	
	def __str__(self):
		"""
		Translate the lobby list item into readable text.
		"""
		text =  "{} ({}x{}, {}/{})".format(
				self.server.name, 
				self.server.boardsize[0], self.server.boardsize[1],
				self.server.num_players[0], self.server.num_players[1])
		return text
	
	def set_server(self, server):
		"""
		Update item contents.
		"""
		self.server = server
		self.set_text(str(self))

	def get_uuid(self):
		"""
		Get the UUID of the item.
		"""
		return self.server.uuid
