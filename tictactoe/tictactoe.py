"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    X_count = 0
    O_count = 0
    for i in range(3):
        X_count += board[i].count(X)
        O_count += board[i].count(O)
    if X_count == O_count:
        return X
    elif X_count > O_count:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    optional_actions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                optional_actions.append((i, j))
    return optional_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if board[i][j] is not None:
        raise ValueError("Illegal move")
    copied_board = copy.deepcopy(board)
    copied_board[i][j] = player(copied_board)
    return copied_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        if (board[i][0] == board[i][1] == board[i][2]) and board[i][0] != EMPTY:
            return board[i][0]
        elif (board[0][i] == board[1][i] == board[2][i]) and board[0][i] != EMPTY:
            return board[0][i]
    if (board[0][0] == board[1][1] == board[2][2]) and board[0][0] != EMPTY:
        return board[0][0]
    elif (board[2][0] == board[1][1] == board[0][2]) and board[2][0] != EMPTY:
        return board[2][0]
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    EMPTY_count = 0
    for i in range(3):
        EMPTY_count += board[i].count(EMPTY)
    # be careful when it is a tie
    if winner(board) or EMPTY_count == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == O:
        action_value = {}
        for action in actions(board):
            value = max_value(result(board, action))
            action_value[action] = value
        for k, v in action_value.items():
            if v == min(action_value.values()):
                return k
    if player(board) == X:
        action_value = {}
        for action in actions(board):
            value = min_value(result(board, action))
            action_value[action] = value
        for k, v in action_value.items():
            if v == max(action_value.values()):
                return k


def max_value(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return utility(board)
    value = -math.inf
    for action in actions(board):
        value = max(value, min_value(result(board, action)))
    return value


def min_value(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return utility(board)
    value = math.inf
    for action in actions(board):
        value = min(value, max_value(result(board, action)))
    return value
