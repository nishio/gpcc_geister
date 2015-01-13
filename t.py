# -*- encoding: utf-8 -*-
from random import choice, shuffle, seed, random
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

class Game(object):
    def __init__(self):
        if BOARD_WIDTH == 4:
            op = [1, 2]
        elif BOARD_WIDTH == 6:
            op = [1, 2, 3, 4, 7, 8, 9, 10]
        else:
            raise NotImplemented
        me = [MAX_POS - pos for pos in op]
        shuffle(op)
        shuffle(me)
        self.val = (me, op)

    @staticmethod
    def rotate(val):
        return [MAX_POS - pos if pos != IS_DEAD else IS_DEAD for pos in val]

    def get_rotated(self, side):
        me = self.val[side][:]
        op = self.val[1 - side][:]
        if side == 1:
            # rotate
            me = Game.rotate(me)
            op = Game.rotate(op)
        return me, op

    def to_view(self, side):
        me, op = self.get_rotated(side)

        # drop hidden data of opponent
        dead_blue = 0
        dead_red = 0
        alive = []
        for pos in get_blue(op):
            if pos == IS_DEAD:
                dead_blue += 1
            else:
                alive.append(pos)
        for pos in get_red(op):
            if pos == IS_DEAD:
                dead_red += 1
            else:
                alive.append(pos)

        return View(side, me, alive, dead_blue, dead_red)

    @staticmethod
    def by_val(side, me, op):
        self = Game()
        if side == 0:
            self.val = (me, op)
        else:
            self.val = (
                Game.rotate(op),
                Game.rotate(me))
        return self

def get_blue(val):
    return val[:NUM_GEISTER / 2]

def get_red(val):
    return val[NUM_GEISTER / 2:NUM_GEISTER]

class View(object):
    def __init__(self, side, me, alive, dead_blue, dead_red):
        self.side = side
        self.me = me
        self.alive = alive
        self.dead_blue = dead_blue
        self.dead_red = dead_red

    def get_blue(self):
        return get_blue(self.me)

    def get_red(self):
        return get_red(self.me)

def do_move(game, side, move, show_detail=False):
    me, op = game.get_rotated(side)  # copied
    i, d = move
    if d == WIN: return WIN
    if show_detail: print board, move
    newpos = me[i] + d
    if newpos in op:
        #print 'killing', newpos
        opi = op.index(newpos)
        op[opi] = IS_DEAD
        # dead end check
        if all(x == IS_DEAD for x in get_blue(op)):
            return WIN
        if all(x == IS_DEAD for x in get_red(op)):
            return LOSE

    me[i] = newpos
    if show_detail: print board
    return Game.by_val(side, me, op)


def print_board(view):
    ret = ['.'] * (BOARD_WIDTH * BOARD_WIDTH)
    for pos in view.get_blue():
        if pos != IS_DEAD:
            ret[pos] = 'o'
    for pos in view.get_red():
        if pos != IS_DEAD:
            ret[pos] = 'x'
    for pos in view.alive:
        ret[pos] = 'v'

    print '\n'.join(
        ''.join(ret[i * BOARD_WIDTH:(i + 1) * BOARD_WIDTH])
        for i in range(BOARD_WIDTH))
    print 'o' * view.dead_blue, 'x' * view.dead_red
    print

def get_my_blue(board):
    return board[:NUM_GEISTER / 4]

def swap_turn(board):
    board = [MAX_POS - pos if pos != IS_DEAD else IS_DEAD for pos in board]
    board = board[NUM_GEISTER:] + board[:NUM_GEISTER]
    return board




def to_xy(pos):
    return (pos % BOARD_WIDTH, pos / BOARD_WIDTH)

def find_possible_move(view):
    ret = []
    me = view.me
    for i, pos in enumerate(me):
        if pos == IS_DEAD: continue
        x, y = to_xy(pos)
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






class AI(object):
    def __repr__(self):
        return self.__class__.__name__

    def choice(self, board):
        "board -> (index, direction/WIN)"

class Random(AI):
    def choice(self, board):
        moves = find_possible_move(board)
        return choice(moves)


def is_blue(i):
    return i < NUM_GEISTER / 4

def is_red(i): return not is_blue(i)

class Fastest(AI):
    "自分のゴールインまでの手数を短くする"
    def choice(self, board):
        moves = find_possible_move(board)
        if moves[0][1] == WIN: return moves[0]
        scored_moves = defaultdict(list)
        for move in moves:
            # 勝てるなら勝つ
            if move[1] == WIN: return move
            i, d = move
            if is_red(i): continue
            # 本当は正確には「自分の駒が道を塞いでいる」効果を求めるために
            # きちんと最短パスを計算するべきだが、このAIでは省略

            def calc_dist(pos):
                x, y = to_xy(pos)
                return y + min(x, 3 - x)

            blue = get_my_blue(g)
            blue[i] += d
            dist = min(calc_dist(pos) for pos in blue)
            #print "dist", move, dist
            scored_moves[dist].append(move)
        return choice(scored_moves[min(scored_moves)])

class FastestP(AI):
    "epsilon greedy"
    def __init__(self, p):
        self.p = p
    def choice(self, board):
        moves = find_possible_move(board)
        if random() < self.p:
            return choice(moves)
        return Fastest().choice(board)


MAX_TURNS = 300
def match(p1, p2, show_detail=True, record=True):
    "match p1 and p2, return p1's WIN/LOSE/EVEN"
    g = Game()
    #print g
    for i in range(MAX_TURNS):
        v = g.to_view(0)
        if show_detail:
            print p1
            print_board(v)
        move = p1.choice(v)
        #print move
        g = do_move(g, 0, move)
        if g == WIN: return WIN
        if g == LOSE: return LOSE
        if show_detail:
            print_board(v)

        v = g.to_view(1)
        if show_detail:
            print p2
            print_board(v)
        move = p2.choice(v)
        #print move
        g = do_move(g, 1, move)
        if g == WIN: return LOSE
        if g == LOSE: return WIN
        if show_detail:
            print_board(v)

    return EVEN


while True:
    print match(Random(), Random())

#print Counter(match(Random(), Fastest()) for x in range(1000))
#print Counter(match(Fastest(), Random()) for x in range(1000))

#match(Fastest(), FastestP(p=0.1))
