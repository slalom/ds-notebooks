import numpy as np
import tkinter as tk
import copy
import pickle as pickle    # cPickle is available in Python 2.x only, otherwise use pickle

from dots_and_boxes import Game, HumanPlayer, ComputerPlayer, QPlayer

#Q = pickle.load(open("Q_epsilon_09_Nepisodes_200000.p", "rb"))

player_one = HumanPlayer("Player 1", "blue", "X")
#player_two = HumanPlayer("Player 2", "red", "O")
#player_one = ComputerPlayer("Player 1", "red", "O")
player_two = QPlayer("Player 2", "red", "O")



root = tk.Tk()
root.title('Dots and Boxes')

game = Game(root, player_one, player_two, size_board=4)

root.mainloop()