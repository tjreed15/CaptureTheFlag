import json

class Player:

	VISIBLE_DISTANCE = 50
	CONTACT_DISTANCE = 5

	def __init__(self, conn):
		self.conn = conn
		self.creator = False
		self.captain = False
		self.team = -1
		self.pos = [0, 0]
		self.dx = 0
		self.dy = 0
		self.visible_distance_sq = Player.VISIBLE_DISTANCE**2
		self.contact_distance_sq = Player.CONTACT_DISTANCE**2
		self.flag = None
		self.jail = 0
		self.visible = []
		self.move_dist = 1

	def __str__(self):
		return json.dumps({'type': 'player', 'pos': self.pos, 'team': self.team})


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
			'width': width, 'height': height, 'contact_distance': Player.CONTACT_DISTANCE, 
			'visible_distance': Player.VISIBLE_DISTANCE, 'jail_time': wait_time*n_turns_in_jail}))

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

	def set_visibility(self, items):
		self.visible = []
		for item in items:
			if self._dist_sq(item) < self.visible_distance_sq:
				self.visible.append(item)

	def get_contact(self, items):
		touching = []
		for item in items:
			if self._dist_sq(item) < self.contact_distance_sq:
				touching.append(item)
		return touching

	def on_own_side(self, xmax, ymax):
		return self.pos[1] > self.team * ymax/2.0 and  self.pos[1] < (self.team + 1) * ymax/2.0

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

