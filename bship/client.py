#!/usr/bin/python
import pika
import sys, pygame
import logging
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

class Client():
	def __init__(self):
		self.init_log("BShip")
		self.online = False
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

	def init_gfx(self):
		"""
		Initialize graphics.
		"""
		self.log.info("Initializing graphics")
		self.window = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Battleship Client")

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
				s_board = self.gameboard.render()

				if self.player.is_placing_ships():
					mpos = pygame.mouse.get_pos()
					mpos = (mpos[0] - 16, mpos[1] - 16)
					self.gameboard.update_cursor(self.player, mpos)
					self.gameboard.render_cursor(s_board, self.player)

				self.window.blit(s_board, (16, 16))

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.online = False
					elif event.type == pygame.MOUSEBUTTONDOWN:
						if event.button == 1:
							self.gameboard.clicked(self.player, mpos)
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_SPACE:
							self.gameboard.rotate_ship()
						elif event.key == pygame.K_RETURN:
							self.q_channel.basic_publish(exchange="", routing_key="lobby", body="Dummy Server")
							print("Message sent")

				if pygame.key.get_pressed()[pygame.K_ESCAPE]:
					self.online = False

				# Iterative processing on a blocking connection.
				self.q_connection.process_data_events(time_limit=0)

				self.fps_timer.tick(self.fps_limit)
				pygame.display.flip()
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
