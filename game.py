import copy

import numpy as np
import logging
from tqdm import tqdm
from random import shuffle
log = logging.getLogger(__name__)

class Board():
    '''
    Author: Eric P. Nichols
    Date: Feb 8, 2008.
    Board class.
    Board data:
    1=white, -1=black, 0=empty
    '''

    def __init__(self, n):
        "Set up initial board configuration."

        self.n = n
        # Create the empty board array.
        self.pieces = [[0] * self.n for _ in range(2)]
        self.paishan = [i for i in range(self.n)] * 4
        shuffle(self.paishan)

        for i in range(14):
            pai = self.paishan[i]
            assert(pai >= 0 and pai < self.n)
            self.pieces[0][pai] += 1

        self.idx = 14

    # add [][] indexer syntax to the Board
    # def __getitem__(self, index):
    #     return self.pieces[index]

    def has_legal_moves(self):
        return self.idx < 4 * self.n

class OthelloGame():
    def __init__(self, n):
        self.n = n

    def getInitBoard(self):
        b = Board(self.n)
        return b

    def getBoardSize(self):
        # (a,b) tuple
        return (2, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n

    def getNextState(self, board, player, action):
        board.pieces[0][action] -= 1
        board.pieces[1][action] += 1
        next = board.paishan[board.idx]
        board.idx += 1
        board.pieces[0][next] += 1
        return (board, player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0] * self.n
        for i in range(self.n):
            if board.pieces[0][i] > 0:
                valids[i] = 1
        return np.array(valids)

    def getGameEnded(self, board):
        # return None if not ended, 1 if player won, -1 if player lost, 0 if draw.
        b = board

        win = 1
        for i in range(self.n):
            if b.pieces[0][i] in (0, 2, 4):
                continue
            else:
                win = 0
                break
        if win:
            return 1

        if b.has_legal_moves():
            return None
        else:
            return 0

    def stringRepresentation(self, board):
        return str(board.pieces)

    @staticmethod
    def display(board):
        print("-----------------------")
        for i in range(len(board.pieces[0])):
            for j in range(board.pieces[0][i]):
                print("[{}]".format(i), end="")
        print("")
        print("-----------------------")

class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a

class GreedyOthelloPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        for i in range(board.n):
            if board.pieces[0][i] in (0, 2, 4):
                continue
            return i
        return 0

class HumanOthelloPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        # display(board)
        valid = self.game.getValidMoves(board, 1)
        for i in range(len(valid)):
            if valid[i]:
                print("[{}]".format(i), end="")
        while True:
            input_move = input()
            try:
                x = int(input_move)
                if ((0 <= x) and (x < board.n)):
                    a = x
                    if valid[x]:
                        break
            except ValueError:
                'Invalid integer'
        return a


class Arena():
    """
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, player2, game, display=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it. Is necessary for verbose
                     mode.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.display = display

    def playGame(self, verbose=False):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2, 0 if draw)
        """
        board = self.game.getInitBoard()

        b2 = Board(board.n)
        b2.pieces = copy.deepcopy(board.pieces)
        b2.paishan = copy.deepcopy(board.paishan)
        b2.idx = board.idx

        it = 0
        while self.game.getGameEnded(board) is None:
            it += 1
            action = self.player1(board)
            valids = self.game.getValidMoves(board, 1)
            assert valids[action] > 0
            if verbose:
                print("Turn ", str(it), "Player 1 ", end="")
                for i in range(len(board.pieces[0])):
                    for j in range(board.pieces[0][i]):
                        print("[{}]".format(i), end="")
                print("--->[{}]".format(action))
                print("-----------------------")
            board, curPlayer = self.game.getNextState(board, 1, action)
        if verbose:
            for i in range(len(board.pieces[0])):
                for j in range(board.pieces[0][i]):
                    print("[{}]".format(i), end="")
            print("")
        result1 = self.game.getGameEnded(board)
        it1 = it

        board = b2
        it = 0
        while self.game.getGameEnded(board) is None:
            it += 1
            action = self.player2(board)
            valids = self.game.getValidMoves(board, 1)
            assert valids[action] > 0
            if verbose:
                print("Turn ", str(it), "Player 2 ", end="")
                for i in range(len(board.pieces[0])):
                    for j in range(board.pieces[0][i]):
                        print("[{}]".format(i), end="")
                print("--->[{}]".format(action))
                print("-----------------------")
            board, curPlayer = self.game.getNextState(board, 1, action)
        if verbose:
            for i in range(len(board.pieces[0])):
                for j in range(board.pieces[0][i]):
                    print("[{}]".format(i), end="")
            print("")
        result2 = self.game.getGameEnded(board)
        it2 = it

        if result1 == 1 and result2 == 0:
            return 1
        if result1 == 0 and result2 == 1:
            return -1
        if result1 == 0 and result2 == 0:
            return 0
        if it1 < it2:
            return 1
        if it1 > it2:
            return -1
        return 0

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """

        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in tqdm(range(num), desc="Arena.playGames"):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == 1:
                oneWon += 1
            elif gameResult == -1:
                twoWon += 1
            else:
                draws += 1

        return oneWon, twoWon, draws