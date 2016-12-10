#!/usr/bin/python
import pika
import sys, pygame

class Client():
	def __init__(self):
		self.online = False
		self.window = None
		self.fps_limit = 30.0

		pygame.init()
	
	def init_gfx(self):
		self.window = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Battleship Client")

	def init_mq(self):
		self.q_connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
		self.q_channel = self.q_connection.channel()
		self.q_state = self.q_channel.queue_declare(queue="lobby", passive=True)
		self.q_channel.basic_consume(self.mq_callback, queue="lobby", no_ack=True)

	def mq_callback(self, ch, method, properties, body):
		print(" RECV: %r" % body)
	
	def start(self):
		try:
			self.init_gfx()
			self.init_mq()
			self.fps_timer = pygame.time.Clock()

			self.online = True
			while self.online:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.online = False

				if pygame.key.get_pressed()[pygame.K_ESCAPE]:
					self.online = False
				elif pygame.key.get_pressed()[pygame.K_SPACE]:
					self.q_channel.basic_publish(exchange="", routing_key="lobby", body="Dummy Server")
					print("Message sent")

				# Iterative processing on a blocking connection.
				if self.q_channel._consumer_infos:
					self.q_channel.connection.process_data_events(time_limit=0)

				self.fps_timer.tick(self.fps_limit)
		except Exception as e:
			print(e)
		finally:
			self.q_connection.close()
			pygame.quit()

def main():
	client = Client()
	client.start()

if __name__ == '__main__':
	main()
