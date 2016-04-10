import sys, os
import socket
from thread import *
import json
from Tkinter import *
from window import Window


class Client:

	def __init__(self, sock, window):
		self.sock = sock
		self.window = window
		self.team = -1

	# Returns tuple of (cmd, {JSON object of data})
	def decode_message(self, msg):
		try:
			first_space = msg.index(' ')
			return msg[:first_space], json.loads(msg[first_space:])
		except:
			return msg, {}

	# Recieves data from socket
	def recieve_data(self):
		while 1:
			data = self.sock.recv(1024) #recieve_data(s)
			if data == '':
				self.sock.close()
				print 'Connection closed by foreign host.'
				sys.exit(0)
			
			
			cmd, data = self.decode_message(data)
			if cmd == 'init':
				self.team = data['team']
				self.window.set_start_data(data['creator'], data['width'], data['height'],
					data['visible_distance'], data['contact_distance'])
			elif cmd == 'player':
				self.window.display(data['pos'], self.team, data['visible'], data['flag'])
			elif cmd == 'jail':
				self.window.display(None, self.team, [], False)
			elif cmd == 'over':
				print 'Winner: Team', data['winner']
				window.quit()
			elif cmd == 'error':
				if data['code'] == 1:
					self.window.quit()
				print 'error: ', data['msg']


if __name__ == '__main__':
	# Check args: python server.py PORT 
	if not len(sys.argv) in [3]:
		print 'Usage: python {} HOST PORT'.format(sys.argv[0])
		sys.exit(1)

	host = sys.argv[1]
	port = int(sys.argv[2])

	# Create socket and bind to local host and given port
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((host, port))
	except socket.error as msg:
		print 'Connection failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()

	# Create a window
	window = Window(sock)

	# Create new client obj with the socket and window
	client = Client(sock, window)

	# Start listening for server data
	start_new_thread(client.recieve_data, ())

	# Start graphics loop
	window.mainloop()
			
		


