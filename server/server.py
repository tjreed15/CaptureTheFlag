"""
A server to play the game of capture the flag.
"""
__author__ = "TJ Reed"
__copyright__ = "Copyright 2016"
__credits__ = ["Sat Garcia"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "TJ Reed"
__email__ = "tjreed@sandiego.edu"

import sys
import socket
from time import sleep
from thread import *
from capture import Capture
from player import Player
import json
import os

""" Constants """
DEFAULT_PORT = 5555

""" Constants """
# None

""" Globals """
GAME = Capture()
ALL_CONNECTIONS = []

"""
Returns tuple formatted as follows:
(did-recv-data. data)
"""
def recieve_data(conn):
	try:
		# Receiving from client
		data = conn.recv(1024)
		return True, data.strip()
	except socket.error, e:
		return False, -1

# Returns tuple of (cmd, {JSON object of data})
def decode_message(msg):
	try:
		first_space = msg.index(' ')
		return msg[:first_space], json.loads(msg[first_space:])
	except:
		return msg, {}

def join_game(player):
	global GAME
	return GAME.add_player(player)


def wait_for_start(player, conn):
	while not GAME.started: 
		available, data = recieve_data(conn)
		if available:
			cmd, data = decode_message(data)
			if player.creator and cmd == 'start':
				GAME.start()
			elif cmd == '':
				print 'Player Disconnected: ' + player.ip + ':' + player.port
				if player.creator:
					print "Game reset"
					GAME.__init__()
				sys.exit(0)


def play_game(player, conn):
	while True:
		available, data = recieve_data(conn)
		if available:
			cmd, data = decode_message(data)
			if cmd == 'move':
				player.request_move(int(data['x']), int(data['y']))
			elif cmd == '':
				print 'Player Disconnected: ' + player.ip + ':' + player.port
				sys.exit(0)

# Function for handling connections. This will be used to create threads
def client_thread(conn, ip, port):
	try:
		# Create this player
		player = Player(conn, ip, port)

		# Attempt to join the game
		if not join_game(player):
			conn.close()
			sys.exit(0)

		# Wait until creator starts the game
		wait_for_start(player, conn)

		# Clear all messages that were sent while waiting for start
		recieve_data(conn)

		# During gameplay
		play_game(player, conn)

		# Close connection when game is over
		conn.close()
	except Exception as e:
		print e
		# If this player is the last in the game, reset the game
		print 'Disconnected with: ' + ip + ':' + port
		global GAME
		if len(GAME.teams[0]) + len(GAME.teams[1]) == 1:
			GAME.__init__()

		# Close connection and exit 
		conn.close()
		sys.exit(1)



if __name__ == '__main__':
	host = ''
	port = int(os.environ.get("PORT", DEFAULT_PORT))


	# Create socket, bind to local host and given port, and listen
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		s.bind((host, port))
		s.listen(10)
		s.setblocking(False)
	except socket.error as msg:
		print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
	
	print 'Server running at localhost:{}'.format(port)
 
	# now keep talking with the client
	while 1:
		try:
			#wait to accept a connection - blocking call
			conn, addr = s.accept()
			print 'Connected with ' + addr[0] + ':' + str(addr[1])
		 
			# start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
			start_new_thread(client_thread, (conn, addr[0], str(addr[1])))
			ALL_CONNECTIONS.append(conn)
		except socket.error, e:
			# Should be a blocking call for accept, but need to do
			#  non-blocking socket for recv'ing messages later on
			continue
		except KeyboardInterrupt:
			s.close()
			print 'Exiting due to keyboad interrupt' 
			sys.exit(0)
 
