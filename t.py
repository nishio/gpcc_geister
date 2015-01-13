from random import choice, shuffle, seed
from copy import copy
seed(1234)

## mini-geister
IS_MINI_BOARD = False
if IS_MINI_BOARD:
    NUM_GEISTER = 2
    BOARD_WIDTH = 4
else:
    NUM_GEISTER = 8
    BOARD_WIDTH = 6

MAX_POS = BOARD_WIDTH * BOARD_WIDTH - 1
IS_DEAD = MAX_POS + 1

UP = -BOARD_WIDTH
DOWN = BOARD_WIDTH
RIGHT = 1
LEFT = -1

WIN = 'WIN'
LOSE = 'LOSE'

def make_new_game():
    if BOARD_WIDTH == 4:
        op = [1, 2]
    elif BOARD_WIDTH == 6:
        op = [1, 2, 3, 4, 7, 8, 9, 10]
    else:
        raise NotImplemented
    me = [MAX_POS - pos for pos in op]
    shuffle(op)
    shuffle(me)
    return me + op

def find_possible_move(board):
    ret = []
    me = board[:NUM_GEISTER]
    for i, pos in enumerate(me):
        if pos == IS_DEAD: continue
        x = pos % BOARD_WIDTH
        y = pos / BOARD_WIDTH
        if y != 0 and pos + UP not in me:
            ret.append((i, UP))
        if y !=  BOARD_WIDTH - 1 and pos + DOWN not in me:
            ret.append((i, DOWN))
        if x != 0 and pos + RIGHT not in me:
           ret.append((i, RIGHT))
        if x != BOARD_WIDTH - 1 and pos + LEFT not in me:
           ret.append((i, LEFT))

        if (x == 0 or x == BOARD_WIDTH - 1) and y == 0 and i < NUM_GEISTER / 2:
            return WIN

    return ret

def print_board(board):
    ret = ['.'] * (BOARD_WIDTH * BOARD_WIDTH)
    for pos in board[:NUM_GEISTER / 2]:
        if pos != IS_DEAD:
            ret[pos] = 'o'
    for pos in board[NUM_GEISTER / 2:NUM_GEISTER]:
        if pos != IS_DEAD:
            ret[pos] = 'x'
    for pos in board[NUM_GEISTER:]:
        if pos != IS_DEAD:
            ret[pos] = 'v'

    print '\n'.join(
        ''.join(ret[i * BOARD_WIDTH:(i + 1) * BOARD_WIDTH])
        for i in range(BOARD_WIDTH)) 


def do_move(board, move):
    board = copy(board)
    op = board[NUM_GEISTER:]
    i, d = move
    print board, move
    newpos = board[i] + d
    if newpos in op:
        i = op.index(newpos)
        board[i + NUM_GEISTER] = IS_DEAD
        # dead end check
        if all(x == IS_DEAD for x in board[NUM_GEISTER:NUM_GEISTER + NUM_GEISTER / 2]):
            return "WIN"
        if all(x == IS_DEAD for x in board[NUM_GEISTER + NUM_GEISTER / 2:]):
            return "LOSE"

    board[i] = newpos
    print board
    return board

def swap_turn(board):
    board = [MAX_POS - pos if pos != IS_DEAD else IS_DEAD for pos in board]
    board = board[NUM_GEISTER:] + board[:NUM_GEISTER]
    return board


g = make_new_game()

while True:
    print_board(g)    
    moves = find_possible_move(g)
    if moves == WIN: break
    move = choice(moves)
    g = do_move(g, move)
    if g == WIN: break
    if g == LOSE: break
    print_board(g)    
    g = swap_turn(g)
    print
