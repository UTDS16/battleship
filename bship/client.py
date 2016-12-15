#!/usr/bin/python
import pika
import uuid, time
import pickle
import sys, pygame
import logging
from collections import OrderedDict

import ocempgui.widgets as ow
import ocempgui.widgets.Constants as oc
import ocempgui.events as oe

import board.board as bb
import protocol as bp
import player as bpl
import events as be
from gui.gui import GUI

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

class Client():
	S_LOBBY = 0
	S_CREATE = 1
	S_JOIN = 2
	S_GAME = 3

	MSG_TIMEOUT = 3

	M_ANNOUNCE = 0

	def __init__(self):
		self.init_log("BShip")
		self.online = False
		self.state = be.S_LOBBY
		self.hosting = False
		self.window = None
		self.fps_limit = 30.0

		self.uuid = str(uuid.uuid4())
		self.log.info("UUID: " + self.uuid)

		self.server_list = OrderedDict()

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
		self.window = self.renderer.screen

		self.gui = GUI(self.renderer)
		self.gui.show_lobby()

	def init_mq(self):
		"""
		Initialize the message queue connection.
		"""
		self.log.info("Connecting to RabbitMQ")
		self.q_connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
		self.q_channel = self.q_connection.channel()
		self.q_state = self.q_channel.queue_declare(queue="lobby")
		self.q_channel.basic_consume(self.mq_callback, queue="lobby")

	def do_announce(self):
		self.log.debug("Announcing game server")

		# TODO:: Move to a protocol module
		msg_dict = {
				"id": self.M_ANNOUNCE,
				"uuid": self.uuid,
				"boardsize": (self.gameboard.w, self.gameboard.h),
				"num_players": self.num_players,
				"name": self.game_name
				}
		msg = bp.Message.pickle(msg_dict)
		self.q_channel.basic_publish(exchange="", routing_key="lobby", body=msg)

	def mq_callback(self, ch, method, properties, body):
		# TODO:: Have a timestamp field as well, and check against current time.

		try:
			msg = bp.Message.unpickle(body)

			# Skip stale messages.
			if hasattr(msg, "timestamp") and time.time() - msg.timestamp < Client.MSG_TIMEOUT:
				if msg.id == self.M_ANNOUNCE:
					self.server_list[msg.uuid] = msg
		except ValueError as e:
			# Ignore "insecure string pickle",
			# which comes from incompatible. 
			pass
		except Exception as e:
			self.log.exception(e)
	
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
				# Process server list while in the lobby,
				if self.state == be.S_LOBBY:
					self.gui.process_serverlist(self.server_list)
				# Render gameboard, if in the right mode.
				elif self.state == be.S_GAME:
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

				# Handle events.
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.online = False
					elif event.type == be.E_ANNOUNCE:
						self.do_announce()
					# A change in the game state?
					elif event.type == be.E_STATE:
						self.state = event.state
						if self.state == be.S_GAME:
							# Are we hosting the game?
							if event.hosting:
								self.hosting = True
								# Announce the game in the lobby.
								pygame.time.set_timer(be.E_ANNOUNCE, 1000)

							# Initialize the game board.
							self.game_name = event.name
							self.gameboard = bb.GameBoard(
									event.boardsize[0], event.boardsize[1])
							self.num_players = event.num_players
							# Initialize our player.
							self.player = bpl.Player()
							self.player.start_placing_ships()
					else:
						# In game state?
						if self.state == Client.S_GAME:
							if event.type == pygame.MOUSEBUTTONDOWN:
								self.gameboard.clicked(self.player, mpos)
							elif event.type == pygame.KEYDOWN:
								if event.key == pygame.K_SPACE:
									self.gameboard.rotate_ship()
						
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
