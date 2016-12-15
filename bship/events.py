import pygame

# It seems that up to USEREVENT + 3 are already taken.
# Anyway, an event for server announces.

# It's about time for the server to advertise its presence.
E_ANNOUNCE = pygame.USEREVENT + 4
# A state change has occurred.
E_STATE = pygame.USEREVENT + 5

# Player in the lobby.
S_LOBBY = 0
# Player creating a new server.
S_CREATE = 1
# Player joining an existing game.
S_JOIN = 2
# Player in the game.
S_GAME = 3
# Player in the game, placing ships.
S_GAME_PLACING = 4
# Player in the game, waiting for their turn.
S_GAME_WAITING = 5
# Player's turn, cherry-picking the tile to bomb.
S_GAME_SHOOTING = 6

S_GAME_LAST = 6
