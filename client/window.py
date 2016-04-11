from Tkinter import Tk, BOTH, Canvas, ALL
from ttk import Frame, Button, Style
import json

class Player:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def move(self, dx, dy):
		self.x += dx
		self.y += dy

class Window(Tk):

	''' Constants '''
	PLAYER_RADIUS = 5
	VISIBLE_RADIUS = 50
	BG_COLOR = 'grey'
	VISIBLE_COLOR = 'white'
	TEAM_COLORS = ['blue', 'green']

	
	def __init__(self, sock):
		Tk.__init__(self)
		self.sock = sock

		# Make screen full size (the window grows for somereason without the "-1")
		self.config(width=self.winfo_screenwidth()-1, height=self.winfo_screenheight()-1)

		# Bind key events
		self.bind('<Left>', self.leftKey)
		self.bind('<Right>', self.rightKey)
		self.bind('<Up>', self.upKey)
		self.bind('<Down>', self.downKey)
		self.bind('<Escape>', lambda event: self.quit())


		# Set title, canvas, and player
		self.title('Capture the Flag')
		self.update()
		self.canvas = Canvas(self, width=self.winfo_width(), height=self.winfo_height(), 
			borderwidth=1, highlightthickness=0, bg=Window.BG_COLOR)
		self.canvas.pack(fill='both', expand=True)

		# Move window to the front
		self.bring_to_front()

	# Empty canvas, resize if user has resized window
	def reset_canvas(self):
		self.canvas.delete(ALL)
		# self.canvas.grid()

	# TODO: Change this method to add start button
	def set_start_data(self, creator, width, height, visible_dist, contact_dist):
		if creator:
			self.bind('<space>', lambda event: self.start_game())
		self.field_width = width
		self.field_height = height
		self.visible_dist = visible_dist
		self.contact_dist = contact_dist


	# Loop through visible players/flags and draw them
	# TODO: change display if player has flag or is in jail
	def display(self, pos, team, visible, has_flag):
		self.reset_canvas()

		# Set offset to draw objects at (center on screen)
		self.offset_x = (self.winfo_width() - self.field_width) / 2
		self.offset_y = (self.winfo_height() - self.field_height) / 2

		# Draw bounds of field & midline
		self._draw_rect(self.field_width/2, self.field_height/4, self.field_width, 
			self.field_height/2, fill=Window.TEAM_COLORS[0])
		self._draw_rect(self.field_width/2, 3*self.field_height/4, self.field_width, 
			self.field_height/2, fill=Window.TEAM_COLORS[1])

		# If in jail, dont show anything else
		if not pos or pos[0] < 0 or pos[1] < 0:
			return

		# Draw the player/visible area to the screen 
		self._draw_oval(pos[0], pos[1], self.visible_dist, fill=Window.VISIBLE_COLOR)
		self._draw_oval(pos[0], pos[1], self.contact_dist, fill=Window.TEAM_COLORS[team])

		# Draw other visible objects
		for item in visible:
			item = json.loads(item)
			if item['type'] == 'player':
				self._draw_oval(item['pos'][0], item['pos'][1], item['size'], 
					fill=Window.TEAM_COLORS[item['team']])
			elif item['type'] == 'flag':
				self._draw_rect(item['pos'][0], item['pos'][1], item['size']*2, 
					item['size']*2, fill=Window.TEAM_COLORS[item['team']])


	# Bring the window to the front
	def bring_to_front(self):
		self.lift()
		self.call('wm', 'attributes', '.', '-topmost', True)
		self.after_idle(self.call, 'wm', 'attributes', '.', '-topmost', False)

	# Send request to move player to the left
	def leftKey(self, event):
		self.sock.send('move {}\n'.format(json.dumps({'x': -1, 'y': 0})))

	# Send request to move player to the right
	def rightKey(self, event):
		self.sock.send('move {}\n'.format(json.dumps({'x': 1, 'y': 0})))

	# Send request to move player up
	def upKey(self, event):
		self.sock.send('move {}\n'.format(json.dumps({'x': 0, 'y': -1})))

	# Send request to move player down
	def downKey(self, event):
		self.sock.send('move {}\n'.format(json.dumps({'x': 0, 'y': 1})))

	# Send request to start game
	def start_game(self):
		self.sock.send('start\n')

	def _draw_oval(self, x, y, r, *args, **kwargs):
		x += self.offset_x
		y += self.offset_y
		self.canvas.create_oval(x-r, y-r, x+r, y+r, *args, **kwargs)

	def _draw_rect(self, x, y, w, h, *args, **kwargs):
		x += self.offset_x
		y += self.offset_y
		self.canvas.create_rectangle(x-w/2, y-h/2, x+w/2, y+h/2, *args, **kwargs)


def main():
	class FakeSocket:
		def send(self, msg):
			print msg,

	sock = FakeSocket()

	win = Window(sock)
	win.allow_to_start()
	win.display([100, 100], 0, [
			{'type': 'player', 'pos': [50, 50], 'team': 1}, 
			{'type': 'flag', 'pos': [150, 50], 'team': 1},
			{'type': 'player', 'pos': [250, 50], 'team': 0}, 
			{'type': 'flag', 'pos': [350, 50], 'team': 0} 
		], False)
	win.mainloop()

if __name__ == '__main__':
	main()
