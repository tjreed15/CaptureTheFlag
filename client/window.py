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
	CANVAS_WIDTH_RATIO = 0.8
	CANVAS_HEIGHT_RATIO = 0.8
	PLAYER_RADIUS = 5
	VISIBLE_RADIUS = 50
	BG_COLOR = 'grey'
	VISIBLE_COLOR = 'white'
	TEAM_COLORS = ['blue', 'green']

	
	def __init__(self, sock):
		Tk.__init__(self)
		self.sock = sock

		# Make screen full size
		self.config(width=self.winfo_screenwidth(), height=self.winfo_screenheight())

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
		self.player = Player(self.winfo_width()/2, self.winfo_height()/2)

		# Move window to the front
		self.bring_to_front()

	# Empty canvas, resize if user has resized window
	def reset_canvas(self):
		self.canvas.delete(ALL)
		self.canvas.config(width=self.winfo_width(), height=self.winfo_height())
		self.canvas.grid()

	# TODO: Change this method to add start button
	def allow_to_start(self):
		self.bind('<space>', lambda event: self.start_game())
	# # Create frame with start button
	# def wait_for_players(self, creator):
	# 	if creator:
	# 		self.reset_canvas()
	# 		start_button = Button(self, text='Start', command=self.start_game)
	# 		start_button.place(x=50, y=50)
	# 	# TODO: Add text saying waiting for players


	# Loop through visible players/flags and draw them
	# TODO: change display if player has flag
	def display(self, pos, team, visible, has_flag):
		self.reset_canvas()

		# Draw the player/visible area to the screen 
		self.canvas.create_oval(pos[0]-Window.VISIBLE_RADIUS, pos[1]-Window.VISIBLE_RADIUS, 
			pos[0]+Window.VISIBLE_RADIUS, pos[1]+Window.VISIBLE_RADIUS, fill=Window.VISIBLE_COLOR)
		self.canvas.create_oval(pos[0]-Window.PLAYER_RADIUS, pos[1]-Window.PLAYER_RADIUS, 
			pos[0]+Window.PLAYER_RADIUS, pos[1]+Window.PLAYER_RADIUS, fill=Window.TEAM_COLORS[team])

		# Draw other visible objects
		for item in visible:
			item = json.loads(item)
			typ = item['type']
			x = item['pos'][0]
			y = item['pos'][1]
			team = item['team']
			if typ == 'player':
				self.canvas.create_oval(x-Window.PLAYER_RADIUS, y-Window.PLAYER_RADIUS, 
					x+Window.PLAYER_RADIUS, y+Window.PLAYER_RADIUS, fill=Window.TEAM_COLORS[team])
			elif typ == 'flag':
				self.canvas.create_rectangle(x-Window.PLAYER_RADIUS, y-Window.PLAYER_RADIUS, 
					x+Window.PLAYER_RADIUS, y+Window.PLAYER_RADIUS, fill=Window.TEAM_COLORS[team])


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
		self.sock.send('move {}\n'.format(json.dumps({'x': 0, 'y': 1})))

	# Send request to move player down
	def downKey(self, event):
		self.sock.send('move {}\n'.format(json.dumps({'x': 0, 'y': -1})))

	# Send request to start game
	def start_game(self):
		self.sock.send('start\n')


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
