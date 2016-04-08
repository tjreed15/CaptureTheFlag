import json

class Flag:

	def __init__(self, team, x, y):
		self.team = team
		self.pos = [x, y]

	def __str__(self):
		return json.dumps({'type': 'flag', 'pos': self.pos, 'team': self.team})