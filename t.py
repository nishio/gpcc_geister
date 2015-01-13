# -*- encoding: utf-8 -*-
from random import choice, shuffle, seed
from copy import copy
from collections import defaultdict, Counter
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
EVEN = 'EVEN'

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
        if x != 0 and pos + LEFT not in me:
           ret.append((i, LEFT))
        if x != BOARD_WIDTH - 1 and pos + RIGHT not in me:
           ret.append((i, RIGHT))

        if (x == 0 or x == BOARD_WIDTH - 1) and y == 0 and i < NUM_GEISTER / 2:
            return [(i, WIN)]  # 上がれる手があるときにはそれだけを候補とする

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


def do_move(board, move, show_detail=False):
    board = copy(board)
    op = board[NUM_GEISTER:]
    i, d = move
    if d == WIN: return WIN
    if show_detail: print board, move
    newpos = board[i] + d
    if newpos in op:
        #print 'killing', newpos
        opi = op.index(newpos)
        board[opi + NUM_GEISTER] = IS_DEAD
        # dead end check
        if all(x == IS_DEAD for x in board[NUM_GEISTER:NUM_GEISTER + NUM_GEISTER / 2]):
            return WIN
        if all(x == IS_DEAD for x in board[NUM_GEISTER + NUM_GEISTER / 2:]):
            return LOSE

    board[i] = newpos
    if show_detail: print board
    return board

def swap_turn(board):
    board = [MAX_POS - pos if pos != IS_DEAD else IS_DEAD for pos in board]
    board = board[NUM_GEISTER:] + board[:NUM_GEISTER]
    return board


class AI(object):
    def __repr__(self):
        return self.__class__.__name__

    def choice(self, board):
        "board -> (index, direction/WIN)"

class Random(AI):
    def choice(self, board):
        moves = find_possible_move(board)
        return choice(moves)


#def is_blue(i):
#    return i < NUM_GEISTER / 4

class Fastest(AI):
    "自分のゴールインまでの手数を短くする"
    def choice(self, board):
        moves = find_possible_move(board)
        if moves[0][1] == WIN: return moves[0]
        scored_moves = defaultdict(list)
        for move in moves:
            # 勝てるなら勝つ
            if move[1] == WIN: return move
            # 本当は正確には「自分の駒が道を塞いでいる」効果を求めるために
            # きちんと最短パスを計算するべきだが、このAIでは省略
            g = do_move(board, move)

            # 勝てるなら勝つ
            if g == WIN: return move
            # 負ける手は避ける
            if g == LOSE: continue  # 負ける手しか打てないレアケースがあるのでよくない

            def calc_dist(pos):
                x = pos % 4
                y = pos / 4
                return y + min(x, 3 - x)

            dist = min(calc_dist(pos) for pos in g[:NUM_GEISTER / 4])
            scored_moves[dist].append(move)
        return choice(scored_moves[min(scored_moves)])

MAX_TURNS = 300
def match(p1, p2, show_detail=True):
    "match p1 and p2, return p1's WIN/LOSE/EVEN"
    g = make_new_game()
    for i in range(MAX_TURNS):
        if show_detail:
            print p1
            print_board(g)
            print
        move = p1.choice(g)
        g = do_move(g, move)
        if g == WIN: return WIN
        if g == LOSE: return LOSE
        if show_detail: print_board(g)
        g = swap_turn(g)
        if show_detail: print

        if show_detail:
            print p2
            print_board(g)
            print
        move = p2.choice(g)
        g = do_move(g, move)
        if g == WIN: return LOSE
        if g == LOSE: return WIN
        if show_detail: print_board(g)
        g = swap_turn(g)
        if show_detail: print

    return EVEN


while True:
    print match(Fastest(), Fastest())
