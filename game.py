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

    # list of all 8 directions on the board, as (x,y) offsets
    __directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]

    def __init__(self, n):
        "Set up initial board configuration."

        self.n = n
        # Create the empty board array.
        self.pieces = [[0] * 37 for _ in range(2)]

        paishan = [i for i in range(37)] * 4
        shuffle(paishan)
        for i in range(14):
            pai = paishan[i]
            assert(pai >= 0 and pai < 37)
            self.pieces[0][pai] += 1

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.pieces[index]

    def countDiff(self, color):
        """Counts the # pieces of the given color
        (1 for white, -1 for black, 0 for empty spaces)"""
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==color:
                    count += 1
                if self[x][y]==-color:
                    count -= 1
        return count

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black)
        """
        moves = set()  # stores the legal moves.

        # Get all the squares with pieces of the given color.
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==color:
                    newmoves = self.get_moves_for_square((x,y))
                    moves.update(newmoves)
        return list(moves)

    def has_legal_moves(self, color):
        all = np.array([4] * 37)
        cur = np.array(self.pieces[0]) + np.array(self.pieces[1])
        return not np.array_equal(cur, all)

    def get_moves_for_square(self, square):
        """Returns all the legal moves that use the given square as a base.
        That is, if the given square is (3,4) and it contains a black piece,
        and (3,5) and (3,6) contain white pieces, and (3,7) is empty, one
        of the returned moves is (3,7) because everything from there to (3,4)
        is flipped.
        """
        (x,y) = square

        # determine the color of the piece.
        color = self[x][y]

        # skip empty source squares.
        if color==0:
            return None

        # search all possible directions.
        moves = []
        for direction in self.__directions:
            move = self._discover_move(square, direction)
            if move:
                moves.append(move)

        # return the generated move list
        return moves

    def execute_move(self, move, color):
        """Perform the given move on the board; flips pieces as necessary.
        color gives the color of the piece to play (1=white,-1=black)
        """

        #Much like move generation, start at the new piece's square and
        #follow it on all 8 directions to look for a piece allowing flipping.

        flips = [flip for direction in self.__directions
                      for flip in self._get_flips(move, direction, color)]
        assert len(list(flips))>0
        for x, y in flips:
            self[x][y] = color

    def _discover_move(self, origin, direction):
        """ Returns the endpoint for a legal move, starting at the given origin,
        moving by the given increment."""
        x, y = origin
        color = self[x][y]
        flips = []

        for x, y in Board._increment_move(origin, direction, self.n):
            if self[x][y] == 0:
                if flips:
                    return (x, y)
                else:
                    return None
            elif self[x][y] == color:
                return None
            elif self[x][y] == -color:
                flips.append((x, y))

    def _get_flips(self, origin, direction, color):
        """ Gets the list of flips for a vertex and direction to use with the
        execute_move function """
        #initialize variables
        flips = [origin]

        for x, y in Board._increment_move(origin, direction, self.n):
            if self[x][y] == 0:
                return []
            if self[x][y] == -color:
                flips.append((x, y))
            elif self[x][y] == color and len(flips) > 0:
                return flips

        return []

    @staticmethod
    def _increment_move(move, direction, n):
        """ Generator expression for incrementing moves """
        move = list(map(sum, zip(move, direction)))
        #move = (move[0]+direction[0], move[1]+direction[1])
        while all(map(lambda x: 0 <= x < n, move)): 
        #while 0<=move[0] and move[0]<n and 0<=move[1] and move[1]<n:
            yield move
            move=list(map(sum,zip(move,direction)))
            #move = (move[0]+direction[0],move[1]+direction[1])


class OthelloGame():
    square_content = {
        -1: "X",
        +0: "-",
        +1: "O"
    }

    def __init__(self, n):
        self.n = n

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n)
        return b
        #return np.array(b.pieces)

    def getBoardSize(self):
        # (a,b) tuple
        return (2, 37)

    def getActionSize(self):
        # return number of actions
        return 37

    def getNextState(self, board, player, action):
        board.pieces[0][action] -= 1
        board.pieces[1][action] += 1
        
        paishan = []
        for pai in range(37):
            remain = 4 - board.pieces[0][pai] - board.pieces[1][pai]
            for _ in range(remain):
                paishan.append(pai)
        shuffle(paishan)
        next = paishan[0]

        board.pieces[0][next] += 1
        return (board, player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0] * 37
        for i in range(37):
            if board.pieces[0][i] > 0:
                valids[i] = 1
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return None if not ended, 1 if player won, -1 if player lost, 0 if draw.
        b = board

        win = 1
        for i in range(37):
            if b.pieces[0][i] in (0, 2, 4):
                continue
            else:
                win = 0
                break
        if win:
            return 1

        if b.has_legal_moves(player):
            return None
        else:
            return 0

    def stringRepresentation(self, board):
        return str(board.pieces)

    @staticmethod
    def display(board):
        print("-----------------------")
        for i in range(37):
            for j in range(board[0][i]):
                print("[{}]".format(i), end="")
        print("")
        print("-----------------------")

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
                if ((0 <= x) and (x < 37)):
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
        players = [self.player2, None, self.player1]
        curPlayer = 1 # player1 go first
        board = self.game.getInitBoard()
        it = 0
        while self.game.getGameEnded(board, curPlayer) is None:
            it += 1
            if verbose:
                assert self.display
                print("Turn ", str(it), "Player ", str(curPlayer))
                self.display(board)
            action = players[curPlayer + 1](board)

            valids = self.game.getValidMoves(board, 1)

            if valids[action] == 0:
                log.error(f'Action {action} is not valid!')
                log.debug(f'valids = {valids}')
                assert valids[action] > 0
            board, curPlayer = self.game.getNextState(board, curPlayer, action)
        result = curPlayer * self.game.getGameEnded(board, curPlayer)
        if verbose:
            assert self.display
            print("Game over: Turn ", str(it), "Result ", str(result))
            self.display(board)
        return result

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """

        num = int(num / 2)
        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in tqdm(range(num), desc="Arena.playGames (player1 go first)"):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == 1:
                oneWon += 1
            else:
                draws += 1

        self.player1, self.player2 = self.player2, self.player1

        for _ in tqdm(range(num), desc="Arena.playGames (player2 go first)"):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == 1:
                twoWon += 1
            else:
                draws += 1

        return oneWon, twoWon, draws

