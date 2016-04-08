import time
from thread import *
from player import Player
from flag import Flag
import json
import sys


class Capture:

	BOARD_WIDTH = 400.0
	BOARD_HEIGHT = 400.0
	FLAGS = [Flag(0, 0, 0), Flag(1, BOARD_WIDTH, BOARD_HEIGHT)]
	WAIT_TIME = 0.05
	N_TURNS_IN_JAIL = 100 # 5 Seconds
	MOVE_DIST = 5
	
	def __init__(self):
		self.teams = [[], []]
		self.flags = Capture.FLAGS
		self.jail = []
		self.curr_team = 0
		self.started = False

	def __str__(self):
		return 'Game with players:', str(players)

	def add_player(self, player):
		if not self.started:
			player.init_side(self.curr_team, Capture.BOARD_WIDTH, Capture.BOARD_HEIGHT, Capture.MOVE_DIST,
				Capture.WAIT_TIME, Capture.N_TURNS_IN_JAIL, len(self.teams[self.curr_team]) == 0)
			self.teams[self.curr_team].append(player)
			self.curr_team = int(not self.curr_team)
		else:
			error_obj = { 'msg': 'You cannot join the game. It has already started.\n' }
			conn.sendall('error ' + json.dumps(error_obj))
		return not self.started

	def start(self):
		self._init_positions()
		self._send_to_all('start\n')
		start_new_thread(self.main_loop, ())
		self.started = True

	# Winner should be a JSON object
	def game_over(self, team):
		self.started = False
		winner = {'winner': team}
		self._send_to_all('over {}\n'.format(json.dumps(winner)))

	def main_loop(self):
		while True:
			free_players = set(self.teams[0] + self.teams[1]) - set(self.jail)

			# Update position of all players
			for player in free_players:
				player.move(Capture.BOARD_WIDTH-1, Capture.BOARD_HEIGHT-1)

				# Check for a winner
				if player.flag and player.on_own_side(Capture.BOARD_WIDTH, Capture.BOARD_HEIGHT):
					print 'Game over'
					self.game_over(player.team)
					sys.exit(0)

			# Check contact with other players / flags
			contact_lists = []
			flag_lists = []
			for player in free_players:
				contact_lists.append(player.get_contact(set(self.teams[int(not player.team)]) - set(self.jail)))
				flag_lists.append([x for x in player.get_contact(self.flags) if x.team != player.team])

			# Calculate who can see whom, send data to each player
			for i, player in enumerate(free_players):
				# Get lists corrosponding to player
				contact_list = contact_lists[i]
				flag_list = flag_lists[i]

				# Deal with players in contact with other players / flags
				if contact_list and not player.on_own_side(Capture.BOARD_WIDTH, Capture.BOARD_HEIGHT):
					player.go_to_jail()
					self.jail.append(player)

					# Return flag if player was carrying it
					if player.flag:
						self.flags.append(player.flag)
						player.flag = None

				elif flag_list:
					player.caught_flag(flag_list[0])
					self.flags.remove(flag_list[0])

				player.set_visibility(set(self.teams[0] + self.teams[1] + self.flags) - set([player]))
				player.alert()

			# For all players in jail, countdown until they can leave
			for player in self.jail:
				if player.turn_in_jail():
					player.pos = [Capture.BOARD_WIDTH/2, player.team * Capture.BOARD_HEIGHT]
					self.jail.remove(player)

			# Pause for set time
			time.sleep(Capture.WAIT_TIME)


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



