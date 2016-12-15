# battleship
A multiplayer battleship game (second homework).

Not finished, and probably won't be able to finish by the deadline.

## Dependencies
The application depends on the following modules:
* [RabbitMQ](https://www.rabbitmq.com/)
* [OcempGUI-0.2.9](https://sourceforge.net/projects/ocemp/)
* [pika](https://github.com/pika/pika)

## Running it
In order to test it, several instances of the same client should be started. Each instance can be started with the following commands:

    cd bship
    python client.py

One of the clients must be used to create a new game. The next clients can then connect to the game server.

The following are not implemented yet:
* Shooting, checking for hits, 
* Updating score,
* Handling join and leave events on the fly,
* Configuration file support for RabbitMQ server not on localhost.
