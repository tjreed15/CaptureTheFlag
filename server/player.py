import json

class Player:

	''' Constants '''
	VISIBLE_DISTANCE = 50
	CONTACT_DISTANCE = 5

	def __init__(self, conn, ip, port):
		self.conn = conn
		self.ip = ip
		self.port = port
		self.creator = False
		self.captain = False
		self.team = -1
		self.pos = [0, 0]
		self.dx = 0
		self.dy = 0
		self.visible_distance = Player.VISIBLE_DISTANCE
		self.contact_distance = Player.CONTACT_DISTANCE
		self.flag = None
		self.jail = 0
		self.visible = []
		self.move_dist = 1

	def __str__(self):
		return json.dumps({'type': 'player', 'pos': self.pos, 'team': self.team, 'size': self.contact_distance})


	# Alert the user of the updated status
	def alert(self):
		self.conn.sendall('player ' + json.dumps({'pos': self.pos, 
			'visible': [str(x) for x in self.visible], 'flag': self.flag != None}))

	def init_side(self, team, width, height, move_dist, wait_time, n_turns_in_jail, captain):
		self.team = team
		self.move_dist = move_dist
		self.n_turns_in_jail = n_turns_in_jail
		self.captain = bool(captain)
		self.creator = bool(self.captain) and team == 0
		self.conn.sendall('init ' + json.dumps({'creator': self.creator, 'captain': captain, 'team': team,
			'width': width, 'height': height, 'contact_distance': self.contact_distance, 
			'visible_distance': self.visible_distance, 'jail_time': wait_time*n_turns_in_jail}))

	# Normalize input and request move
	def request_move(self, dx, dy):
		self.dx = 0 if dx == 0 else dx/abs(dx) * self.move_dist
		self.dy = 0 if dy == 0 else dy/abs(dy) * self.move_dist

	def move(self, xmax, ymax):
		if self.jail:
			return
		self.pos[0] = min(max(self.pos[0] + self.dx, 0), xmax)
		self.pos[1] = min(max(self.pos[1] + self.dy, 0), ymax)
		self.dx = self.dy = 0

	# Resets visibility list to only players in visibility range
	# Returns list of players in contact with this player
	def set_player_visibility(self, players):
		self.visible = []
		touching = []
		for player in players:
			dist = self._dist_sq(player)
			
			# Check if player is within visible range
			if dist < (self.visible_distance + player.contact_distance) ** 2:
				self.visible.append(player)

				# Check if player is in contact range and is on opposite team
				if (dist < (self.contact_distance + player.contact_distance) ** 2) and self.team != player.team:
					touching.append(player)

		return touching

	# Appends visible flags to visibility list
	# Returns list of flags in contact with this player
	def set_flag_visibility(self, flags):
		touching = []
		for flag in flags:
			dx = abs(self.pos[0] - flag.pos[0])
			dy = abs(self.pos[1] - flag.pos[1])

			# Check if flag is within visible range
			if dx < (self.visible_distance + flag.contact_distance) and dy < (self.visible_distance + flag.contact_distance):
				self.visible.append(flag)

				# Check if flag is in contact range and is on opposite team
				if dx < (self.contact_distance + flag.contact_distance) and dy < (self.contact_distance + flag.contact_distance) and self.team != flag.team:
					touching.append(flag)

		return touching

	def on_own_side(self, xmax, ymax):
		if self.team == 0: 
			return self.pos[1] < ymax/2
		else:
			return self.pos[1] > ymax/2

	def go_to_jail(self):
		self.pos = [-1, -1]
		self.jail = self.n_turns_in_jail
		self.conn.sendall('jail\n')

	def turn_in_jail(self):
		self.jail -= 1
		if self.jail <= 0:
			self.jail = 0
			self.conn.sendall('free\n')
		return self.jail == 0

	def caught_flag(self, flag):
		self.flag = flag
		self.conn.sendall('flag\n')

	def _dist_sq(self, player):
		dx = (self.pos[0] - player.pos[0])
		dy = (self.pos[1] - player.pos[1])
		return dx*dx + dy*dy

