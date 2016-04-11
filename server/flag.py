import json

class Flag:

	''' Constants '''
	CONTACT_DISTANCE = 50

	def __init__(self, team, x, y):
		self.team = team
		self.pos = [x, y]
		self.contact_distance = Flag.CONTACT_DISTANCE

	def __str__(self):
		return json.dumps({'type': 'flag', 'pos': self.pos, 'team': self.team, 'size': self.contact_distance})