"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None

class NotValidAction(Exception):
    """Raised when action is not possible for the board"""
    pass

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def _count(board, symbol):
    """
    Returns the number of a given symbol on the board.
    """
    return sum(row.count(symbol) for row in board)

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if _count(board, X) == _count(board, O):
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    res = set()
    for i in range(len(board)):
        for j in range(len(board)):
            if not board[i][j]:
                res.add((i,j))
    return res


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i = action[0]
    j = action[1]

    #deep copy
    res = [row[:] for row in board]

    #between 0 and len(board) too ?
    if board[i][j]:  
        raise NotValidAction
    
    res[i][j]=player(board)
    return res

def _aligned(board, symbol):
    """
    Returns True is there are 3 of the chosen symbol aligned on the board.
    """
    diagonal1 = True
    diagonal2= True
    for i in range(len(board)):
        if board[i][i] != symbol:
            diagonal1 = False
        if board[i][2-i] != symbol:
                diagonal2 = False

    if diagonal1 or diagonal2:
        return True
    else :
        for i in range(len(board)):
            horizontal = True
            vertical = True
            for j in range(len(board)):
                if board[i][j] != symbol:
                    vertical = False
                if board[j][i] != symbol:
                    horizontal = False
            if vertical or horizontal:
                return True
        return False

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if _aligned(board, X):
        return X 
    elif _aligned(board, O):
        return O
    return None 


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) or _count(board, EMPTY) == 0:
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if _aligned(board, X):
        return 1
    elif _aligned(board, O):
        return -1
    else:
        return 0

def _rec_minimax(board, alpha, beta, myTurn):
    """
    Returns a dictionnary containing the score for a given board,
    by using reccurence to evaluate the outcome of the action in the tree
    """
    if terminal(board):
        return utility(board)

    if myTurn:
        maxEva = -math.inf
        for action in actions(board):
            eva = _rec_minimax(result(board, action), alpha, beta, False)
            maxEva = max(maxEva, eva)
            alpha = max(alpha, maxEva)
            if maxEva >= beta:
                break
        return maxEva

    else:
        minEva = math.inf
        for action in actions(board):
            eva = _rec_minimax(result(board, action), alpha, beta, True)
            minEva = min(minEva, eva)
            beta = min(beta, minEva)
            if minEva <= alpha:
                break
        return minEva

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    else:
        scores = {}
        for action in actions(board):
            scores[action] = _rec_minimax(result(board, action), -math.inf, math.inf, player(board) != X)
        if player(board) == X:
            return max(scores.keys(), key=(lambda new_k: scores[new_k]))
        return min(scores.keys(), key=(lambda new_k: scores[new_k]))


