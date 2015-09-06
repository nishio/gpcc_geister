# -*- encoding: utf-8 -*-
"""
Sample client
"""

"""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port")
parser.add_argument("-s", "--server", default="localhost")

args = parser.parse_args()
print(args)


s = socket.socket(sicket.AF_INET, socket.SOCK_STREAM)
s.connect((args.SERVER, args.PORT))
s.sendall(b'hoge')
data = s.recv(1024)
s.close()
"""

from random import seed
names = "abcdefgh"
NOWHERE = (-1, -1)
BOARD_WIDTH = 6

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
    ['b', 'd', 'c', 'e']
    """
    from random import shuffle
    xs = list(names)
    shuffle(xs)
    return xs[:4]


def make_colormap(reds):
    """
    >>> make_colormap("cdef")
    """
    color_map = dict(zip(names, "BBBBBBBB"))
    color_map.update(dict(zip(reds, "RRRR")))
    return color_map


def get_stub_colormap():
    """
    >>> seed(1234)
    >>> get_stub_colormap()['a']
    'B'
    """
    reds = choose_four_red_ghosts_randomly()
    return make_colormap(reds)


def is_dead(pos):
    return (pos == NOWHERE)


def assert_is_pos(pos):
    if is_dead(pos): return
    x, y = pos
    assert 0 <= x < 6
    assert 0 <= y < 6


def is_near_goal(pos):
    assert_is_pos(pos)
    if pos == (0, 0): return True
    if pos == (5, 0): return True
    return False


def enter_goal(pos):
    assert is_near_goal(pos)
    x, y = pos
    if x == 0: return (-1, 0)
    if x == 5: return (1, 0)
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


def board_to_positions(board):
    """
    >>> board_to_positions(TEST_BOARD)
    [(4, 1), (3, 1), (2, 1), (1, 1), (4, 0), (3, 0), (2, 0), (1, 0), (1, 4), (2, 4), (3, 4), (4, 4), (1, 5), (2, 5), (3, 5), (4, 5)]
    """
    ret = []
    for c in 'abcdefghABCDEFGH':
        pos = board.find(c)
        if pos == -1:
            ret.append(NOWHERE)
        y = pos // (BOARD_WIDTH + 1)
        x = pos % (BOARD_WIDTH + 1)
        ret.append((x, y))
    return ret


def four_moves_from(pos):
    """
    >>> four_moves_from((0, 0))
    [((0, -1), 'N'), ((1, 0), 'E'), ((0, 1), 'S'), ((-1, 0), 'W')]
    """
    assert_is_pos(pos)
    assert not(is_dead(pos))
    x, y = pos
    return [((x, y - 1), 'N'), ((x + 1, y), 'E'),
            ((x, y + 1), 'S'), ((x - 1, y), 'W')]


def is_in_board(pos):
    assert isinstance(pos, tuple)
    x, y = pos
    if x < 0: return False
    if 5 < x: return False
    if y < 0: return False
    if 5 < y: return False
    return True


def occupied_by_my_ghost(pos, mypos):
    return pos in mypos


def take_positions_of_my_ghosts(positions):
    return positions[8:]


def possible_moves(positions, colormap=get_stub_colormap()):
    """
    >>> possible_moves(board_to_positions(TEST_BOARD))
    [((1, 4), 'N'), ((1, 4), 'W'), ((2, 4), 'N'), ((3, 4), 'N'), ((4, 4), 'N'), ((4, 4), 'E'), ((1, 5), 'W'), ((4, 5), 'E')]
    """
    my_positions = take_positions_of_my_ghosts(positions)
    ret = []
    for name, pos in zip(names, my_positions):
        color = colormap[name]
        if is_dead(pos): continue
        if is_near_goal(pos):
            if is_blue(pos):
                return [enter_goal(pos)]

        for newpos, move in four_moves_from(pos):
            if is_in_board(newpos):
                if not occupied_by_my_ghost(newpos, my_positions):
                    ret.append((pos, move))

    return ret


class RandomAI(object):
    def choose_red_ghosts(self):
        reds = choose_four_red_ghosts_randomly()
        self.colormap = make_colormap(reds)
        return reds

    def choose_next_move(self, board):
        from random import choice
        moves = possible_moves(board, self.colormap)
        return choice(moves)


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
