#!/usr/bin/python
import pika
import sys, pygame
import logging
import ocempgui.widgets as ow
import ocempgui.widgets.Constants as oc
import ocempgui.events as oe
import board.board as bb
import player as bp

def init_logging():
	"""
	Initialize logging.
	"""
	log = logging.getLogger("CT")
	log.setLevel(logging.DEBUG)

	# Log to file.
	handler = logging.FileHandler("log_server.txt", encoding="UTF-8")
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)
	# And log to stdout.
	handler = logging.StreamHandler()
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)

	return log

class Client(oe.INotifyable):
	S_LOBBY = 0
	S_CREATE = 1
	S_JOIN = 2
	S_GAME = 3

	def __init__(self):
		self.init_log("BShip")
		self.online = False
		self.state = Client.S_LOBBY
		self.window = None
		self.fps_limit = 30.0

		self.gameboard = bb.GameBoard()
		self.player = bp.Player()
		self.player.start_placing_ships()

		self.log.info("Initializing PyGame")
		pygame.init()

	def init_log(self, prefix):
		"""
		Initialize logging to file and stdout.
		"""
		self.log = logging.getLogger(prefix)
		self.log.setLevel(logging.DEBUG)
		# Log to file.
		handler = logging.FileHandler("log.txt", encoding="UTF-8")
		handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
		self.log.addHandler(handler)
		# And log to stdout.
		handler = logging.StreamHandler()
		handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
		self.log.addHandler(handler)
	
	def do_lobby(self):
		"""
		Leave into the lobby.
		"""
		self.state = Client.S_LOBBY
		self.gfx_hide_all()
		self.gfx_show_lobby()

	def do_create_game(self):
		"""
		Display the game creation window.
		"""
		self.state = Client.S_CREATE
		self.gfx_hide_all()
		self.gfx_show_create()
	
	def do_start_game(self):
		"""
		Start hosting the game.
		"""
		self.state = Client.S_GAME
		self.gfx_hide_all()
		self.renderer.color = (0, 0, 0, 0)

	def do_join_game(self):
		"""
		Join the selected game.
		"""
		self.state = Client.S_GAME
		self.gfx_hide_all()
		self.renderer.color = (0, 0, 0, 0)

	def gfx_hide_all(self):
		"""
		Hide all widgets.
		"""
		self.renderer.clear()

	def gfx_show_lobby(self):
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

		# Add all the widgets.
		self.renderer.add_widget(self.l_servers)
		self.renderer.add_widget(self.li_servers)
		self.renderer.add_widget(self.l_nickname)
		self.renderer.add_widget(self.e_nickname)
		self.renderer.add_widget(self.b_create)
		self.renderer.add_widget(self.b_join)

	def gfx_show_create(self):
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


	def init_gfx(self):
		"""
		Initialize graphics.
		"""
		self.log.info("Initializing graphics")
		self.event_manager = oe.EventManager()

		# TODO:: Could use Frames

		self.renderer = ow.Renderer()
		self.renderer.create_screen(800, 600)
		self.renderer.title = "Battleship Client"
		self.renderer.color = (255, 255, 255, 0)

		self.gfx_show_lobby()

		self.window = self.renderer.screen

	def init_mq(self):
		"""
		Initialize the message queue connection.
		"""
		self.log.info("Connecting to RabbitMQ")
		self.q_connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
		self.q_channel = self.q_connection.channel()
		self.q_state = self.q_channel.queue_declare(queue="lobby")
		self.q_channel.basic_consume(self.mq_callback, queue="lobby")

	def mq_callback(self, ch, method, properties, body):
		print(" RECV: %r" % body)
	
	def notify(self, event):
		print(event)
	
	def start(self):
		"""
		Start the game.
		"""
		try:
			self.init_gfx()
			self.init_mq()

			self.fps_timer = pygame.time.Clock()

			self.online = True
			while self.online:
				# Render gameboard, if in the right mode.
				if self.state == Client.S_GAME:
					s_board = self.gameboard.render()

					if self.player.is_placing_ships():
						mpos = pygame.mouse.get_pos()
						mpos = (mpos[0] - 16, mpos[1] - 16)
						self.gameboard.update_cursor(self.player, mpos)
						self.gameboard.render_cursor(s_board, self.player)

					self.window.blit(s_board, (16, 16))

				# Render OcempGUI
				self.renderer.update()
				self.renderer.refresh()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.online = False
					else:
						# In game state?
						if self.state == Client.S_GAME:
							if event.type == pygame.MOUSEBUTTONDOWN:
								self.gameboard.clicked(self.player, mpos)
							elif event.type == pygame.KEYDOWN:
								if event.key == pygame.K_SPACE:
									self.gameboard.rotate_ship()
						
						#if event.key == pygame.K_RETURN:
						#	self.q_channel.basic_publish(exchange="", routing_key="lobby", body="Dummy Server")
						#	print("Message sent")
					# Pass the event to OcempGUI
					self.renderer.distribute_events((event))

				if pygame.key.get_pressed()[pygame.K_ESCAPE]:
					self.online = False

				# Iterative processing on a blocking connection.
				self.q_connection.process_data_events(time_limit=0)

				self.fps_timer.tick(self.fps_limit)
				pygame.display.update()
		except Exception as e:
			self.log.exception(e)
		finally:
			self.q_connection.close()
			pygame.quit()

def main():
	client = Client()
	client.start()

if __name__ == '__main__':
	main()
