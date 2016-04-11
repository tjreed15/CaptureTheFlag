import time
from thread import *
from player import Player
from flag import Flag
import json
import sys


class Capture:

	BOARD_WIDTH = 400.0
	BOARD_HEIGHT = 400.0
	FLAGS = [
		Flag(0, Flag.CONTACT_DISTANCE, Flag.CONTACT_DISTANCE),
		Flag(1, BOARD_WIDTH-Flag.CONTACT_DISTANCE, 
			 	BOARD_HEIGHT-Flag.CONTACT_DISTANCE)
	]
	WAIT_TIME = 0.05
	N_TURNS_IN_JAIL = 100 # 5 Seconds
	MOVE_DIST = 5
	
	def __init__(self):
		self.teams = [[], []]
		self.flags = list(Capture.FLAGS)
		self.jail = []
		self.curr_team = 0
		self.started = False
		self.creator = None

	def __str__(self):
		return 'Game with players:', str(players)

	def add_player(self, player):
		if not self.started:
			player.init_side(self.curr_team, Capture.BOARD_WIDTH, Capture.BOARD_HEIGHT, Capture.MOVE_DIST,
				Capture.WAIT_TIME, Capture.N_TURNS_IN_JAIL, len(self.teams[self.curr_team]) == 0)
			self.teams[self.curr_team].append(player)
			self.curr_team = int(not self.curr_team)
		else:
			error_obj = { 
				'msg': 'You cannot join the game. It has already started.\n',
				'code': 1
			}
			player.conn.sendall('error ' + json.dumps(error_obj))
		return not self.started

	def start(self):
		self._init_positions()
		self._send_to_all('start\n')
		start_new_thread(self.main_loop, ())
		self.started = True
		print 'New Game Started'

	# Winner should be a JSON object
	def game_over(self, team):
		winner = {'winner': team}
		self._send_to_all('over {}\n'.format(json.dumps(winner)))
		self.__init__()

	def main_loop(self):
		while len(self.teams[0]) + len(self.teams[1]) > 0:
			free_players = set(self.teams[0] + self.teams[1]) - set(self.jail)

			# Update position of all players
			for player in free_players:
				player.move(Capture.BOARD_WIDTH, Capture.BOARD_HEIGHT)

				# Check for a winner
				if player.flag and player.on_own_side(Capture.BOARD_WIDTH, Capture.BOARD_HEIGHT):
					print 'Game over'
					self.game_over(player.team)
					sys.exit(0)

			# Check contact/visiblitly with other players / flags
			for player in free_players:
				contact_list = player.set_player_visibility(set(self.teams[0] + self.teams[1]) 
					- set([player]) -  set(self.jail))
				flag_list = player.set_flag_visibility(self.flags)

				# Deal with players in contact with other players / flags
				if contact_list and not player.on_own_side(Capture.BOARD_WIDTH, Capture.BOARD_HEIGHT):
					player.go_to_jail()
					self.jail.append(player)

					# Return flag if player was carrying it
					if player.flag:
						self.flags.append(player.flag)
						player.flag = None

				# Pickup flag
				elif flag_list:
					player.caught_flag(flag_list[0])
					self.flags.remove(flag_list[0])

				try:
					# Send data to player
					player.alert()
				except:
					# If connection disrupted, remove player from game
					self.teams[player.team].remove(player)

					# If no players left, reset the game and end thread
					if len(self.teams[0]) + len(self.teams[1]) == 0:
						self.__init__()
						print 'Game reset'
						sys.exit(1)

			# For all players in jail, countdown until they can leave
			for player in self.jail:
				if player.turn_in_jail():
					player.pos = [Capture.BOARD_WIDTH/2, player.team * Capture.BOARD_HEIGHT]
					self.jail.remove(player)

			# Pause for set time
			time.sleep(Capture.WAIT_TIME)

		# If all players have quit the game
		self.__init__()
		print 'Game reset'
		sys.exit(0)


	# Msg should already be formatted as 'cmd[ {JSON}]'
	def _send_to_all(self, msg):
		for team in self.teams:
			for player in team:
				player.conn.sendall(msg)

	def _init_positions(self):
		for i, team in enumerate(self.teams):
			n_players = len(team)
			for j, player in enumerate(team):
				x = (j + 0.5) * 1.0/n_players * Capture.BOARD_WIDTH
				y = i * Capture.BOARD_HEIGHT + (1-2*i) * Player.CONTACT_DISTANCE
				player.pos = [x, y]
