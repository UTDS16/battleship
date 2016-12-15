import pygame

import ocempgui.widgets as ow
import ocempgui.widgets.Constants as oc
import ocempgui.events as oe

from lobby_list_item import LobbyListItem
import events as be

class GUI():
	"""
	User Interface windows.
	"""

	def __init__(self, renderer):
		self.renderer = renderer
		self.lobby_visible = False

	def hide_all(self):
		"""
		Hide all widgets.
		"""
		self.lobby_visible = False
		self.renderer.clear()

	def show_lobby(self):
		"""
		Display the lobby window.
		"""
		# Get a rectangle with amargin.
		rect = self.renderer._get_rect()
		rect = (rect[0] + 16, rect[1] + 16, rect[2] - 16, rect[3] - 16)

		# Nickname textbox.
		self.e_nickname = ow.Entry("Anon")
		self.e_nickname.topleft = (rect[0] + 64, rect[3] - self.e_nickname.height)
		self.l_nickname = ow.Label("Nickname: ")
		self.l_nickname.topleft = (rect[0], self.e_nickname.topleft[1] + (self.e_nickname.height - self.l_nickname.height) / 2 )

		# Create Game button.
		self.b_create = ow.Button("Create Game")
		self.b_create.topleft = (rect[2] - self.b_create.width - 100, rect[3] - self.b_create.height)
		self.b_create.connect_signal(oc.SIG_CLICKED, self.do_create_game)

		# Join Game button.
		self.b_join = ow.Button("Join Game")
		self.b_join.topleft = (rect[2] - self.b_join.width, rect[3] - self.b_join.height)
		self.b_join.connect_signal(oc.SIG_CLICKED, self.do_join_game)

		# List of servers.
		self.l_servers = ow.Label("List of available servers:")
		self.l_servers.topleft = (rect[0], rect[1])
		self.li_servers = ow.ScrolledList(rect[2] - 16, rect[3] - 64)
		self.li_servers.topleft = (rect[0], rect[1] + 16)
		self.li_servers.set_selectionmode(oc.SELECTION_SINGLE)

		# Add all the widgets.
		self.renderer.add_widget(self.l_servers)
		self.renderer.add_widget(self.li_servers)
		self.renderer.add_widget(self.l_nickname)
		self.renderer.add_widget(self.e_nickname)
		self.renderer.add_widget(self.b_create)
		self.renderer.add_widget(self.b_join)
		
		self.lobby_visible = True

	def show_create(self):
		"""
		Display the window for creating a new game.
		"""
		# Get a rectangle with amargin.
		rect = self.renderer._get_rect()
		rect = (rect[0] + 16, rect[1] + 16, rect[2] - 16, rect[3] - 16)

		self.f_tab = ow.Table(4, 2)
		self.f_tab.topleft = (rect[0], rect[1])

		# Name of the game textbox.
		self.e_gamename = ow.Entry("Ship Wreckyard")
		self.l_gamename = ow.Label("Name of the game: ")
		self.f_tab.add_child(0, 0, self.l_gamename)
		self.f_tab.add_child(0, 1, self.e_gamename)

		# Number of players.
		self.e_players = ow.Entry("3")
		self.l_players = ow.Label("Number of players: ")
		self.f_tab.add_child(1, 0, self.l_players)
		self.f_tab.add_child(1, 1, self.e_players)

		# Board size.
		self.l_boardw = ow.Label("Board width: ")
		self.e_boardw = ow.Entry("10")
		self.l_boardh = ow.Label("Board height: ")
		self.e_boardh = ow.Entry("10")
		self.f_tab.add_child(2, 0, self.l_boardw)
		self.f_tab.add_child(2, 1, self.e_boardw)
		self.f_tab.add_child(3, 0, self.l_boardh)
		self.f_tab.add_child(3, 1, self.e_boardh)

		# Create Game button.
		self.b_cancel = ow.Button("Cancel")
		self.b_cancel.topleft = (rect[2] - self.b_cancel.width - 100, rect[3] - self.b_cancel.height)
		self.b_cancel.connect_signal(oc.SIG_CLICKED, self.do_lobby)

		# Cancel button.
		self.b_create = ow.Button("Start Game")
		self.b_create.topleft = (rect[2] - self.b_create.width, rect[3] - self.b_create.height)
		self.b_create.connect_signal(oc.SIG_CLICKED, self.do_start_game)

		# Add all the widgets.
		self.renderer.add_widget(self.f_tab)
		self.renderer.add_widget(self.b_create)
		self.renderer.add_widget(self.b_cancel)

	def do_lobby(self):
		"""
		Leave into the lobby.
		"""
		event = pygame.event.Event(be.E_STATE, {"state":be.S_LOBBY})
		pygame.event.post(event)

		self.hide_all()
		self.show_lobby()

	def do_create_game(self):
		"""
		Display the game creation window.
		"""
		event = pygame.event.Event(be.E_STATE, {"state":be.S_CREATE})
		pygame.event.post(event)

		self.hide_all()
		self.show_create()
	
	def do_start_game(self):
		"""
		Start hosting the game.
		"""
		d = {"state": be.S_GAME,
				"hosting": True,
				"uuid": None,
				"name": self.e_gamename.text,
				"num_players": (1, int(self.e_players.text)),
				"boardsize": (int(self.e_boardw.text), int(self.e_boardh.text))}
		event = pygame.event.Event(be.E_STATE, d)
		pygame.event.post(event)

		self.hide_all()
		self.renderer.color = (0, 0, 0, 0)

	def do_join_game(self):
		"""
		Join the selected game.
		"""
		item = self.li_servers.get_selected()[0]
		d = {"state": be.S_GAME,
				"hosting": False,
				"name": item.server.name,
				"num_players": item.server.num_players,
				"boardsize": item.server.boardsize}
		event = pygame.event.Event(be.E_STATE, d)

		self.hide_all()
		self.renderer.color = (0, 0, 0, 0)

	def process_serverlist(self, serverlist):
		"""
		Process the announcements collected from the message queue.
		"""
		# Note that events may be late.
		# However, mustn't work on widgets that are being
		# garbage collected.
		if not self.lobby_visible:
			return

		num_servers = 0
		for key, val in serverlist.iteritems():
			# Either update an existing list item.
			if len(self.li_servers.items) > 0 and num_servers < len(self.li_servers.items):
				self.li_servers.items[num_servers].set_server(val)
			# Or create a new one.
			else:
				self.li_servers.items.append(LobbyListItem(val))
			num_servers += 1

