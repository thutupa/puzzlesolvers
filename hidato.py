import sys

digit_chars = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

stop_chars = set(['.', 'X', '\n'])

interesting_chars = digit_chars | stop_chars

def tokenizer(inp):
    curtok = ''
    i = 0
    while i < len(inp):
        cur = inp[i]
        i += 1
        if cur not in interesting_chars:
            if curtok:
                i -= 1
                yield curtok
                curtok = ''
            continue
        if cur in stop_chars:
            if curtok:
                yield curtok
                curtok = ''
            yield cur
            continue
        curtok += cur
    if curtok: yield curtok

assert [x for x in tokenizer('123')] == ['123']

assert [x for x in tokenizer('123.')] == ['123', '.']

assert [x for x in tokenizer('123 .')] == ['123', '.']

assert [x for x in tokenizer('123;.')] == ['123', '.']

assert [x for x in tokenizer('123;.X')] == ['123', '.', 'X']

assert [x for x in tokenizer('123;.X\n')] == ['123', '.', 'X', '\n']

b = '.'
no = 'X'
e = 'E'

def pad_to_longest(rows):
    l = 0
    for r in rows: l = max(l, len(r))
    for ri, r in enumerate(rows):
        rows[ri] = r + ([e] * (l - len(r)))  # rjust

def parse_puzzle(inp):
    row = []
    rows = []
    for v in tokenizer(inp):
        if v == '\n':
            if row:
                row.append(e)
                rows.append(row)
                row = []
        elif v == '.' or v == 'X':
            if not row: row.append(e)
            row.append(v)
        else:
            if not row: row.append(e)
            row.append(int(v))
    if row:
        row.append(e)
        rows.append(row)
    pad_to_longest(rows)
    rows = [[e] * len(rows[0])] + rows + [[e] * len(rows[0])]
    return rows

def puzzle_equal(p1, p2):
    for ri, r in enumerate(zip(p1, p2)):
        r1, r2 = r
        for ci, c in enumerate(zip(r1, r2)):
            c1, c2 = c
            if c1 != c2:
                sys.stderr.write("Fail at %d, %d, %s, %s %r %r" % (ri, ci, c1, c2, r1, r2))
                return False
    return True

assert puzzle_equal(parse_puzzle('123'),
                    [[e, e, e],
                     [e, 123, e],
                     [e, e, e]])

assert puzzle_equal(parse_puzzle(
    '''
.  33 35 . .
X 3 4
'''), [
    [e, e, e, e, e, e, e],
    [e, b, 33, 35, b, b, e],
    [e, no, 3, 4, e],
    [e, e, e, e, e]])

# From: http://rosettacode.org/wiki/Solve_a_Hidato_puzzle
test_puzzle = (
'''.  33 35 . .
. . 24 22 .
. . . 21 . .
. 26 . 13 40 11
27 . . . 9 . 1
X X . . 18 . .
X X X X . 7 . .
X X X X X X 5 .''')  # Trailing newline should get added

assert puzzle_equal(parse_puzzle(test_puzzle),
    [
        [e, e, e, e, e, e, e],
        [e, b, 33, 35, b, b, e,],
        [e, b, b, 24, 22, b, e],
        [e, b, b, b, 21, b, b, e],
        [e, b, 26, b, 13, 40, 11, e],
        [e, 27, b, b, b, 9, b, 1, e],
        [e, no, no, b, b, 18, b, b, e],
        [e, no, no, no, no, b, 7, b, b, e],
        [e, no, no, no, no, no, no, 5, b, e],
        [e, e, e, e, e, e, e, e, e, e]])

class Solved(BaseException): pass

def all_cells(puzzle):
    for ri, r in enumerate(puzzle):
        if ri == 0 or ri == (len(puzzle)-1): continue
        for ci, c in enumerate(r):
            if ci == 0 or ci == (len(puzzle) -1): continue
            yield ((ri, ci), c)
def print_puzzle(puzzle):
    for ri, r in enumerate(puzzle):
        for ci, c in enumerate(r):
            if c == e: continue
            if c == b:
                p = ' '
            else:
                p = str(c)
            print(p.rjust(3), end='')
        print()
                
def value_at(puzzle, cell):
    ri, ci = cell
    return puzzle[ri][ci]

def set_value(puzzle, cell, value):
    ri, ci = cell
    puzzle[ri][ci] = value

def clear_value(puzzle, cell):
    set_value(puzzle, cell, b)

def find_cell_with_value(puzzle, value):
    for p, v in all_cells(puzzle):
        if v == value:
            return p
    return None

TERMINAL_VALUE = 40  # Should be improved.

def neighbors(puzzle, cell):
    ri, ci = cell
    
    nrs = []
    for xd in [-1, 0, 1]:
        for yd in [-1, 0, 1]:
            if xd == 0 and yd == 0: continue
            nc = (ri + xd, ci + yd)
            v = value_at(puzzle, nc)
            if v != e and v != no:
                nrs.append(nc)
    return nrs

def find_neighbor_with_value(puzzle, cell, value):
    for nc in neighbors(puzzle, cell):
        if value_at(puzzle, nc) == value:
            return nc
    return None

def solve(puzzle):
    cell = find_cell_with_value(puzzle, 1)
    assert cell
    try:
	search_solution(puzzle, cell)
    except Solved: return
    print "Could not find a solution!!"

def search_solution(puzzle, cell):
    v = value_at(puzzle, cell)
    if v == TERMINAL_VALUE:
        print_puzzle(puzzle)
        raise Solved()
        return
    nc = find_neighbor_with_value(puzzle, cell, v+1)
    if nc:
        search_solution(puzzle, nc)
    else:
        for n in neighbors(puzzle, cell):
            if value_at(puzzle, n) == b:
                set_value(puzzle, n, v+1)
                search_solution(puzzle, n)
                clear_value(puzzle, n)

solve(parse_puzzle(test_puzzle))
