# -*- encoding: utf-8 -*-
"""
Sample client
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", default=10000)
parser.add_argument("-s", "--server", default="localhost")
parser.add_argument("--endless-test", action='store_true')
parser.add_argument("-t", "--test", action='store_true')
args = parser.parse_args()

from random import seed, choice
names = "abcdefgh"
FULL_NAMES = "ABCDEFGHabcdefgh"
NOWHERE = (9, 9)
BOARD_WIDTH = 6
DIRECTION_INFO = """
 N    K
W E  H L
 S    J
"""

TEST_BOARD = """
.hgfe.
.dcba.
......
......
.ABCD.
.EFGH.
""".strip()


def choose_four_red_ghosts_randomly():
    """choose 4 red ghosts randomly
    >>> seed(1234)
    >>> choose_four_red_ghosts_randomly()
    ['f', 'c', 'b', 'g']
    """
    from random import shuffle
    xs = list(names)
    shuffle(xs)
    return xs[:4]


def make_colormap(reds):
    """
    >>> make_colormap("cdef") == {'a': 'B', 'e': 'R', 'g': 'B', 'b': 'B', 'd': 'R', 'c': 'R', 'f': 'R', 'h': 'B'}
    True
    """
    color_map = dict(zip(names, "BBBBBBBB"))
    color_map.update(dict(zip(reds, "RRRR")))
    return color_map


def get_test_colormap():
    seed(1234)
    reds = choose_four_red_ghosts_randomly()
    return make_colormap(reds)
TEST_COLORMAP = get_test_colormap()


def is_in_board(p):
    assert_is_pair_of_int(p)
    x, y = p
    if x < 0: return False
    if 5 < x: return False
    if y < 0: return False
    if 5 < y: return False
    return True


def is_near_goal(pos):
    assert_is_pos(pos)
    if pos == (0, 0): return True
    if pos == (5, 0): return True
    return False


def assert_is_ghost(x):
    assert isinstance(x, Ghost)


def enter_goal(ghost):
    assert_is_ghost(ghost)
    assert is_near_goal(ghost.pos)
    x, y = ghost.pos
    if x == 0: return (ghost, 'W')
    if x == 5: return (ghost, 'E')
    raise AssertionError('not here')


def go_ahead(pos):
    """
    return candidates to go ahead to the goal
    >>> go_ahead((3, 3))
    [(1, 0), (0, -1)]
    >>> go_ahead((2, 3))
    [(-1, 0), (0, -1)]
    >>> go_ahead((2, 0))
    [(-1, 0)]
    """
    assert_is_pos(pos)
    x, y = pos
    candidates = []
    if x < 3:
        if 0 < x:
            candidates.append((-1, 0))
    else:
        if x < 5:
            candidates.append((1, 0))
    if 0 < y:
        candidates.append((0, -1))

    return candidates


def occupied_by_my_ghost(pos, mypos):
    return pos in mypos


from collections import namedtuple
Ghost = namedtuple("Ghost", "name pos color")

TEST_GHOSTS = [Ghost('A', (1, 4), 'R'), Ghost('B', (2, 4), 'R'), Ghost('C', (3, 4), 'R'), Ghost('D', (4, 4), 'R'), Ghost('E', (1, 5), 'B'), Ghost('F', (2, 5), 'B'), Ghost('G', (3, 5), 'B'), Ghost('H', (4, 5), 'B'), Ghost('a', (4, 1), 'u'), Ghost('b', (3, 1), 'u'), Ghost('c', (2, 1), 'u'), Ghost('d', (1, 1), 'u'), Ghost('e', (4, 0), 'u'), Ghost('f', (3, 0), 'u'), Ghost('g', (2, 0), 'u'), Ghost('h', (1, 0), 'u')]
TEST_MESSAGE = "14R24R34R44R15B25B35B45B41u31u21u11u40u30u20u10u"
def message_to_ghosts(message):
    """
    >>> message_to_ghosts(TEST_MESSAGE) == TEST_GHOSTS
    True
    """
    assert len(message) == 48
    ghosts = []
    for i in range(16):
        c1, c2, c3 = message[i * 3:i * 3 + 3]
        name = FULL_NAMES[i]
        pos = (int(c1), int(c2))
        color = c3
        ghosts.append(Ghost(name, pos, color))
    return ghosts


def take_my_ghosts(ghosts):
    return ghosts[:8]


def test1():
    """
    >>> test1()
    'A,N'
    """
    message = TEST_MESSAGE
    ghosts = message_to_ghosts(message)
    moves = possible_moves(ghosts)
    move = moves[0]
    return move_to_str(move)


def assert_is_direction(x):
    assert x in "NEWS"


def move_to_str(move):
    """
    >>> move_to_str((Ghost("A", (0, 0), "B"), "N"))
    'A,N'
    """
    assert_is_move(move)
    ghost, direction = move
    return "{},{}".format(ghost.name, direction)


def assert_is_move(move):
    assert isinstance(move, tuple) and len(move) == 2
    ghost, direction = move
    assert_is_ghost(ghost)
    assert_is_direction(direction)


def connect_server(ai=None):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.server, int(args.port)))

    data = s.recv(1024)
    assert data == "SET?\r\n"

    if ai:
        p = ai()
    else:
        p = FastestAI()

    reds = p.choose_red_ghosts()
    reds = ''.join(reds).upper()
    msg = "SET:{}\r\n".format(reds)
    s.send(msg)

    while True:
        data = s.recv(1024)
        if not data.startswith('MOV?'):
            assert any(data.startswith(x) for x in ["WON", "LST", "DRW"])
            if True:  # TODO: option
                print data[:3]
            break

        msg = data[4:]
        if len(msg) > 48: msg = msg[:48]
        ghosts = message_to_ghosts(msg)
        move = p.choose_next_move(ghosts)
        msg = "MOV:{}\r\n".format(move_to_str(move))
        s.send(msg)
    s.close()


def run_random_player():
    import subprocess
    import os
    FNULL = open(os.devnull, 'w')
    subprocess.Popen(
        "cd ../geister_server.java;"
        " java -cp build/libs/geister.jar net.wasamon.geister.player.RandomPlayer localhost 10001"
        " &> /dev/null", shell=True, stdout=FNULL, stderr=FNULL)


def endless_random_test():
    while True:
        run_random_player()
        connect_server()


def _test():
    import doctest
    doctest.testmod()


class AI(object):
    def __repr__(self):
        return self.__class__.__name__


class RandomAI(AI):
    def choose_red_ghosts(self):
        reds = choose_four_red_ghosts_randomly()
        return reds

    def choose_next_move(self, ghosts):
        from random import choice
        moves = possible_moves(ghosts)
        return choice(moves)


class FastestRedAI(AI):
    "自分のゴールインまでの手数を(赤を青とみなして)短くする"
    def choose_red_ghosts(self):
        reds = choose_four_red_ghosts_randomly()
        return reds

    def choose_next_move(self, ghosts):
        moves = possible_moves(ghosts)
        from collections import defaultdict
        scored_moves = defaultdict(list)
        def calc_dist(pos):
            x, y = pos
            return y + min(x, 3 - x)

        for move in moves:
            ghost, d = move
            if is_blue(ghost):
                dist = 1000
            else:
                newpos = calc_new_pos(ghost.pos, d)
                dist = calc_dist(newpos)
            scored_moves[dist].append(move)
        return choice(scored_moves[min(scored_moves)])


class FastestAI(AI):
    "自分のゴールインまでの手数を短くする"
    def choose_red_ghosts(self):
        reds = choose_four_red_ghosts_randomly()
        return reds

    def choose_next_move(self, ghosts):
        moves = possible_moves(ghosts)
        from collections import defaultdict
        scored_moves = defaultdict(list)
        def calc_dist(pos):
            x, y = pos
            return y + min(x, 3 - x)

        for move in moves:
            ghost, d = move
            if is_red(ghost):
                dist = 1000
            else:
                newpos = calc_new_pos(ghost.pos, d)
                dist = calc_dist(newpos)
            scored_moves[dist].append(move)
        return choice(scored_moves[min(scored_moves)])


class EpsilonFastestAI(AI):
    "epsilon greedy"
    def __init__(self, p=0.5):
        self.p = p
    def choice(self, ghosts):
        moves = possible_moves(ghosts)
        if random() < self.p:
            return choice(moves)
        return Fastest.choice(self, ghosts)


def is_blue(ghost):
    return ghost.color == 'B' or ghost.color == 'b'


def is_red(ghost):
    return ghost.color == 'R' or ghost.color == 'r'


def calc_new_pos(pos, direction):
    if direction == 'N':
        return (pos[0], pos[1] - 1)
    if direction == 'E':
        return (pos[0] + 1, pos[1])
    if direction == 'W':
        return (pos[0], pos[1] + 1)
    if direction == 'S':
        return (pos[0] - 1, pos[1])
    raise AssertionError('not here')


class TakerAI(AI):
    "取れるときには取る"
    def choose_red_ghosts(self):
        reds = choose_four_red_ghosts_randomly()
        return reds

    def choose_next_move(self, ghosts):
        moves = possible_moves(ghosts)
        from collections import defaultdict
        scored_moves = defaultdict(list)

        for move in moves:
            ghost, d = move
            if is_red(ghost):
                dist = 1000
            else:
                newpos = calc_new_pos(ghost.pos, d)
                dist = calc_dist(newpos)
            scored_moves[dist].append(move)
        return choice(scored_moves[min(scored_moves)])


def red_string(s):
    return "\033[041m%s\033[0m" % s

def blue_string(s):
    return "\033[044m%s\033[0m" % s

def color_ghost_string(g):
    if is_blue(g):
        return blue_string(g.name)
    elif is_red(g):
        return red_string(g.name)
    return g.name

def is_dead_pos(p):
    assert_is_pair_of_int(p)
    return (p == NOWHERE)


def is_dead(g):
    assert_is_ghost(g)
    return (g.pos == NOWHERE)


"""
is_pair_of_int > is_pos = (is_in_board + is_dead_pos)
"""
def assert_is_pair_of_int(p):
    assert isinstance(p, tuple) and len(p) == 2
    x, y = p
    assert isinstance(x, int) and isinstance(y, int)


def assert_is_pos(p):
    assert_is_pair_of_int(p)
    if is_dead_pos(p): return
    x, y = p
    assert is_in_board(p)


def four_moves_from(pos):
    """
    >>> four_moves_from((0, 0))
    [((0, -1), 'N'), ((1, 0), 'E'), ((0, 1), 'S'), ((-1, 0), 'W')]
    """
    assert_is_pos(pos)
    assert is_in_board(pos)
    x, y = pos
    return [((x, y - 1), 'N'), ((x + 1, y), 'E'),
            ((x, y + 1), 'S'), ((x - 1, y), 'W')]


TEST_GHOSTS = message_to_ghosts(TEST_MESSAGE)
def possible_moves(ghosts):
    """
    >>> moves = possible_moves(TEST_GHOSTS)
    >>> moves[0]
    (Ghost(name='A', pos=(1, 4), color='R'), 'N')
    >>> [move_to_str(m) for m in moves]
    ['A,N', 'A,W', 'B,N', 'C,N', 'D,N', 'D,E', 'E,W', 'H,E']
    """
    my_ghosts = take_my_ghosts(ghosts)

    ret = []
    for ghost in my_ghosts:
        if is_dead(ghost): continue
        pos = ghost.pos
        color = ghost.color
        if is_near_goal(pos):
            if is_blue(ghost):
                return [enter_goal(ghost)]

        occupied = [x.pos for x in my_ghosts]
        for newpos, move in four_moves_from(pos):
            if is_in_board(newpos):
                if not occupied_by_my_ghost(newpos, occupied):
                    ret.append((ghost, move))

    return ret


class HumanAI(AI):
    "自分のゴールインまでの手数を短くする"
    def choose_red_ghosts(self):
        reds = choose_four_red_ghosts_randomly()
        return reds

    def choose_next_move(self, ghosts):
        pos2ghosts = dict((x.pos, x) for x in ghosts)
        pretty = ""
        for y in range(6):
            for x in range(6):
                g = pos2ghosts.get((x, y))
                if not g:
                    pretty += '.'
                else:
                    pretty += color_ghost_string(g)
            pretty += "\n"
        print pretty
        print ' '.join(
            color_ghost_string(g)
            for g in ghosts
            if is_dead(g))

        print DIRECTION_INFO
        move = raw_input("move>>")
        r1 = [g for g in ghosts if g.name == move[0]][0]
        r2 = dict(zip('KLHJNEWS', 'NEWSNEWS'))[move[1]]
        return (r1, r2)


if __name__ == "__main__":
    if args.test:
        _test()
    elif args.endless_test:
        endless_random_test()
    else:
        run_random_player()
        connect_server(HumanAI)

