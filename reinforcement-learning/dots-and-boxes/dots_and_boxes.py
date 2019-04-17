# Ryan Croke, 4-10-2019
"""
This is a refactor of some code I found on the internet sorry, no attribution :(
It is intended to be used to build a reinforcement learning algorithm
to master dots and boxes as has been done over and over for tic-tac-toe
"""
import tkinter as tk
from tkinter import font, messagebox
import numpy as np
import copy
import sys
 

class Player(object):
	"""
	The Player class stores the players name, and score and uses the tkinter
	StringVar to immediately update the gui
	"""
	def __init__(self,name,color="black",mark="X"):
		self.human = True
		self.score = 0
		self.players_display_score = ''#= tk.StringVar()
		self.name = name
		self.color = color
		self.mark = mark

	def update(self):
		self.players_display_score = self.name + ": %d" % self.score


class DotsAndBoxesBoard():
	def __init__(self, size_board=4):
		self.TOL = 10
		self.CELLSIZE = 50
		self.OFFSET = 30
		self.CIRCLERAD = 2
		self.DOTOFFSET = self.OFFSET + self.CIRCLERAD
		self.NMBR_ROWS = size_board
		self.GAMEBOARD_SIZE = self.CELLSIZE*(self.NMBR_ROWS-1) + 2*self.OFFSET

		self.dot_center_points = self.dots_center_coordinates()
		self.edge_labels = self.get_edge_labels(self.dot_center_points)
		# should be in the game
		self.available_edges = self.edge_labels
		self.sequence_of_moves = ''

	def dots_center_coordinates(self):
		return [self.CELLSIZE * i + self.OFFSET for i in range(self.NMBR_ROWS)]

	def get_edge_labels(self,center_points):
		"""
		This method finds the midpoint for each edge. These are used as labels
		for each edge and coordinates for computer players to execute
		Sort the edges from top down, left to right
		As the players move, need to keep track of which player took which edge - because
		a player moves twice if player completes a box
		"""
		edge_labels = []
		for i,dot in enumerate(center_points):
		    edge_labels += [(dot,int((center_points[i] + center_points[i+1])/2)) 
		                    for i in range(len(center_points)-1)]
		    edge_labels += [(int((center_points[i] + center_points[i+1])/2),dot) 
		                    for i in range(len(center_points)-1)]
		return sorted(edge_labels, key=lambda tup: tup[0])


	def add_to_sequence_of_moves(self,move,player):
		"""
		move is tuple of midpoint of edge
		mark is player 1 or player 2 - use X and O
		At the end of the game this is the state of the board and each players moves
		"""
		assert isinstance(move,tuple),"can only pass tuples to move sequencing"
		idx_of_move = self.edge_labels.index(move)

		self.sequence_of_moves += str(idx_of_move) + str(player.mark)
		 
		#self.game_move_sequence += str(move[0]) + str(move[1]) + str(player.mark)

	def get_closest_coordinate(self, x, points_list):
		# TODO use halo attribute from tkinter????
		diffs = [abs(x - val) for val in points_list]
		return points_list[diffs.index(min(diffs))]

	def over(self):
		# The game is over when there are no available edges left
		return (not bool(len(self.available_edges)))

	def check_game_over(self, player_one, player_two):
		total = player_one.score + player_two.score

		if total == (self.NMBR_ROWS-1) * (self.NMBR_ROWS-1):
			return True
		else:
			return False

	def determine_winner(self, player_one, player_two):
		if player_one.score == player_two.score:
			return None
		elif player_one.score > player_two.score:
			return player_one.mark
		else:
			return player_two.mark

	def give_reward(self):
		if self.over():
			if self.determine_winner() is not None:
				if self.determine_winner() == "X":
					# Player X won -> positive reward
					return 1.0
				elif self.determine_winner() == "O":
					# Player O won -> negative reward
					return -1.0
			else:
				# A smaller positive reward for cat's game
				return 0.5
		else:
			# No reward if the game is not yet finished
			return 0.0


class Game(tk.Frame):
	def __init__(self, master, player_one, player_two, size_board=4):
		# assert size_board % 2 == 0,"cannot play game that could end in tie"
		self.player_one = player_one
		self.player_two = player_two
		self.human_vs_computer = self.player_one.human + self.player_two.human
		self.size_board = size_board
		
		tk.Frame.__init__(self, master)
		self.board = DotsAndBoxesBoard(self.size_board)

		self.display_font = tk.font.Font(self, name="display_font",
			                             family = "Times", weight="bold",
			                             size=36)
		self.canvas = tk.Canvas(self, height = self.board.GAMEBOARD_SIZE,
			                    width = self.board.GAMEBOARD_SIZE, bg="yellow")
		self.canvas.bind("<Button-1>", lambda e:self.on_screen_click(e))
		self.canvas.grid(row=0,column=0)

		self.dots = [[self.create_circle(self.board.CELLSIZE*i+self.board.OFFSET, 
			          self.board.CELLSIZE*j+self.board.OFFSET,
			          self.board.CIRCLERAD) for j in range(self.board.NMBR_ROWS)] 
		              for i in range(self.board.NMBR_ROWS)]
		self.lines = []
		self.dot_center_points = self.board.dots_center_coordinates()
		self.edge_labels = self.board.get_edge_labels(self.dot_center_points)
		#self.available_edges = self.edge_labels

		self.info_frame = tk.Frame(self)

		self.info_frame.player_one = tk.Label(self.info_frame, 
			                                  textvariable=self.player_one.players_display_score,
			                                  fg=self.player_one.color)
		self.info_frame.player_one.grid()

		self.info_frame.player_two = tk.Label(self.info_frame,
			                                  textvariable=self.player_two.players_display_score,
			                                  fg=self.player_two.color)
		self.info_frame.player_two.grid()

		self.turn = self.player_one
		self.update_players()
		self.info_frame.grid(row = 1, column = 0, sticky = 'N')
		self.grid()

		# if player 1 is computer
		print(self.turn.name)
		if not self.turn.human:
			self.make_computer_move()

	def create_circle(self, x, y, r):
		"""
		center coordinates, radius
		"""
		x0 = x - r
		y0 = y - r
		x1 = x + r
		y1 = y + r
		return self.canvas.create_oval(x0, y0, x1, y1, fill="black")

	def update_players(self):
		self.player_one.update()
		self.player_two.update()

	def update_edge_set(self, start_point, end_point):
		if start_point[1] == end_point[1]:
			move = ( int((start_point[0] + end_point[0]) / 2), start_point[1])
		else:
			move = (start_point[0], int((start_point[1] + end_point[1]) / 2))
		
		#self.available_edges.remove(move)
		self.board.add_to_sequence_of_moves(move,self.turn)
		self.board.available_edges.remove(move)
		#self.board.add_to_sequence_of_moves(move,self.turn)

	def on_screen_click(self, event):
		"""
		This is to capture an on screen event. Check if move or not.
		Do not need horizontal or vertical since edges are unique by
		midpoints
		"""
		x,y = event.x, event.y
		legal_move = self.is_move_legal(x,y)

		if legal_move:
			# legal move but edge may exist
			self.apply_move_to_board((x,y))


	def is_move_legal(self, x, y):
		"""
		If not a "legal move" return None, otherwise
		return tuple (x,y) and go from there
		"""

		limit_small = self.board.OFFSET - self.board.CIRCLERAD
		if (x < limit_small)  or (y < limit_small):
			return None

		limit_large = limit_small + (self.board.NMBR_ROWS-1)*self.board.CELLSIZE
		limit_large += 2*self.board.CIRCLERAD
		if (x > limit_large)  or (y > limit_large):
			return None

		dx = x - self.board.get_closest_coordinate(x,self.dot_center_points)
		dy = y - self.board.get_closest_coordinate(y,self.dot_center_points)

		x -= self.board.OFFSET
		y -= self.board.OFFSET
		dx = x - (x//self.board.CELLSIZE)*self.board.CELLSIZE
		dy = y - (y//self.board.CELLSIZE)*self.board.CELLSIZE

		if np.linalg.norm([dx,dy]) < np.sqrt(self.board.TOL):
			return None

		if abs(dx) < self.board.TOL:
			if abs(dy) < self.board.TOL:
				return None  # mouse in corner of box; ignore
			else:
				return True
		elif abs(dy) < self.board.TOL:
			return True
		else:
			return None

	def apply_move_to_board(self, move):
		# assume (x,y) has already been checked to be on board or not
		
		# line exists?
		if self.does_line_exist(move):
			return None
		
		start_point,end_point = self.construct_edge_from_clicked_move(move)
		line = self.create_line(start_point, end_point)
		score = self.make_new_box(line)
		

		if score:
			self.turn.score += score
			self.turn.update()
			self.check_game_over()
		else:
			if self.turn.name == "Player 1":
				self.turn = self.player_two
			else:
				self.turn = self.player_one

		self.lines.append(line)
		self.update_edge_set(start_point, end_point)

		if not self.turn.human:
			self.make_computer_move()

	def does_line_exist(self, move):
		id_ = self.canvas.find_closest(move[0], move[1], halo=self.board.TOL)[0]
		
		if id_ in self.lines:
			return True
		else:
			return False

	def construct_edge_from_clicked_move(self, move):
		startx = self.get_dot_coordinate_from_click(move[0])
		starty = self.get_dot_coordinate_from_click(move[1])

		if abs(move[0] - startx) > abs(move[1] - starty):
			endx = startx + self.board.CELLSIZE
			endy = starty
		else:
			endx = startx
			endy = starty + self.board.CELLSIZE

		return [(startx,starty), (endx,endy)]

	def create_line(self, point_start, point_end):
		line = self.canvas.create_line(point_start[0], point_start[1], point_end[0], point_end[1])
		return line

	def make_computer_move(self):
		move = self.get_random_move()
		if move: 
			self.apply_move_to_board(move)

	def get_dot_coordinate_from_click(self, coordinate):
		dot_coordinate = self.board.CELLSIZE * ((coordinate-self.board.OFFSET)//self.board.CELLSIZE) 
		dot_coordinate = dot_coordinate + self.board.DOTOFFSET - self.board.CIRCLERAD
		return dot_coordinate

	def make_new_box(self, line):
		score = 0
		x0,y0,x1,y1 = self.canvas.coords(line)

		if x0 == x1:
			midx = x0
			midy = (y0+y1)/2
			pre = (x0 - self.board.CELLSIZE/2, midy)
			post = (x0 + self.board.CELLSIZE/2, midy)

		elif y0 == y1:
			midx = (x0 + x1)/2
			midy = y0
			pre = (midx, y0 - self.board.CELLSIZE/2)
			post = (midx, y0 + self.board.CELLSIZE/2)

		if len(self.find_lines(pre)) == 3:
			self.fill_in_square(pre)
			score += 1

		if len(self.find_lines(post)) == 3:
			self.fill_in_square(post)
			score += 1
		return score

	def find_lines(self, coords):
		x, y = coords
		if x < 0 or x > self.board.GAMEBOARD_SIZE:
			return []
		if y < 0 or y > self.board.GAMEBOARD_SIZE:
			return []

		lines = [x for x in self.canvas.find_enclosed(x-self.board.CELLSIZE,\
                                                      y-self.board.CELLSIZE,\
                                                      x+self.board.CELLSIZE,\
                                                      y+self.board.CELLSIZE)\
				if x in self.lines]
		return lines

	def fill_in_square(self, coords):
		"""
		Given the top left coordinate, fill in square with players color
		"""
		x, y = coords
		startx = self.get_dot_coordinate_from_click(x)
		starty = self.get_dot_coordinate_from_click(y)
		endx = startx + self.board.CELLSIZE
		endy = starty + self.board.CELLSIZE

		return self.canvas.create_rectangle(startx, starty, endx, endy,
			                                fill=self.turn.color)

	def check_game_over(self):
		total = self.player_one.score + self.player_two.score

		if total == (self.board.NMBR_ROWS-1) * (self.board.NMBR_ROWS-1):
			self.canvas.create_text(self.board.GAMEBOARD_SIZE/2, self.board.GAMEBOARD_SIZE/2,
				                    text="GAME OVER", font="display_font", fill="#888")

	#@staticmethod
	def get_random_move(self):
		#print(board.available)
		moves = self.board.available_edges
		if moves:
			return moves[np.random.choice(len(moves))]
		else:
			return None


class ComputerPlayer(Player):
    def __init__(self,name,color="black",mark="X"):
        Player.__init__(self,name,color=color,mark=mark)
        self.human = False

class HumanPlayer(Player):
    pass

class QPlayer(ComputerPlayer):
    def __init__(self, mark, Q={}, epsilon=0.2):
        super(QPlayer, self).__init__(mark=mark)
        self.Q = Q
        self.epsilon = epsilon

    def get_move(self, board):
    	# With probability epsilon, choose a move at random
    	# ("epsilon-greedy" exploration)
        if np.random.uniform() < self.epsilon:
            return ComputerPlayer.get_move(board)
        else:
            state_key = QPlayer.make_and_maybe_add_key(board, self.mark, self.Q)
            Qs = self.Q[state_key]

            if self.mark == "X":
                return QPlayer.stochastic_argminmax(Qs, max)
            elif self.mark == "O":
                return QPlayer.stochastic_argminmax(Qs, min)

    @staticmethod
    # Make a dictionary key for the current state (board + player turn)
    # and if Q does not yet have it, add it to Q
    def make_and_maybe_add_key(board, mark, Q):
    	# Encourages exploration   
    	default_Qvalue = 1.0
    	state_key = board.make_key(mark)

    	if Q.get(state_key) is None:
    		moves = board.available_edges()
    		# The available moves in each state are initially given a default value of zero
    		Q[state_key] = {move: default_Qvalue for move in moves}

    	return state_key

    @staticmethod
    def stochastic_argminmax(Qs, min_or_max):       # Determines either the argmin or argmax of the array Qs such that if there are 'ties', one is chosen at random
        min_or_maxQ = min_or_max(list(Qs.values()))
        if list(Qs.values()).count(min_or_maxQ) > 1:      # If there is more than one move corresponding to the maximum Q-value, choose one at random
            best_options = [move for move in list(Qs.keys()) if Qs[move] == min_or_maxQ]
            move = best_options[np.random.choice(len(best_options))]
        else:
            move = min_or_max(Qs, key=Qs.get)
        return move

if __name__ == '__main__':
	mainw = tk.Tk()
	mainw.title('Dots and Boxes')
	mainw.frm = Game(mainw, Player("Player 1", "blue", "X"), Player("Player 2", "red", "O"))
	mainw.mainloop()