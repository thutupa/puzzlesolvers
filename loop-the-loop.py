# Puzzle is represented as an ajdacency graph The goal is to find a hamiltonian cycle, where each
# vertex has degree two. The plan is to do a DFS on it.
import collections
import random
import time
import sys

# Puzzle is a adjacency list representation of the graph.
class TooManyEdges(BaseException): pass
class CellCapExceeded(BaseException): pass
class Puzzle(object):
    def __init__(self, nrows, ncols):
	self.nrows = nrows
	self.ncols = ncols
	self.cellCounts = collections.defaultdict(lambda: 4)
	self.adj = collections.defaultdict(list)
	self.interestingCells = None
    def neighbors(self, n):
	ret = []
	for off in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
	    n1 = (n[0] + off[0], n[1] + off[1])
	    if n1[0] >= 0 and n1[0] < self.nrows and \
	       n1[1] >= 0 and n1[1] < self.ncols:
	       ret.append(n1)
	return ret

    def addEdge(self, n1, n2):
	n1n = self.adj[n1]
	n2n = self.adj[n2]
	if len(n1n) >= 2 or len(n2n) >= 2:
	    raise TooManyEdges()
	if n2 in n1n or n1 in n2n:
	    assert False #this should not happen
	c1, c2 = self.getAdjacentCells(n1, n2)
	c1c, c2c = self.getCount(c1), self.getCount(c2)
	if c1c == 0 or c2c == 0:
	    raise CellCapExceeded()
	# Okay, we have decided to add the edge
	c1c, c2c = c1c - 1, c2c - 1
	n1n.append(n2)
	n2n.append(n1)
	self.adj[n1] = n1n
	self.adj[n2] = n2n
	self.setCount(c1, c1c)
	self.setCount(c2, c2c)

    def removeEdge(self, n1, n2):
	n1n = self.adj[n1]
	n2n = self.adj[n2]
	assert n2 in n1n and n1 in n2n
	c1, c2 = self.getAdjacentCells(n1, n2)
	c1c, c2c = self.getCount(c1), self.getCount(c2)
	assert c1c < 4 and c2c < 4
	c1c, c2c = c1c + 1, c2c + 1
	n1n.remove(n2)
	n2n.remove(n1)
	self.adj[n1] = n1n
	self.adj[n2] = n2n
	self.setCount(c1, c1c)
	self.setCount(c2, c2c)

    def edgeExists(self, n1, n2):
	return n1 in self.adj[n2] and n2 in self.adj[n1]

    def degree(self, n):
	return len(self.adj[n])

    def getCount(self, c):
	return self.cellCounts[c]

    def setCount(self, c, ct):
	self.cellCounts[c] = ct

    def freezePuzzle(self):
	self.interestingCells = self.cellCounts.keys()

    def isSolved(self):
	for c in self.interestingCells:
	    if self.cellCounts[c] != 0:
		return False
	return True

    def getAdjacentCells(self, n1, n2):
	if n1[0] == n2[0]:
	    # Same row, horizontal edge
	    assert abs(n1[1] - n2[1]) == 1
	    r = n1[0]
	    c1 = max(n1[1], n2[1])
	    return ((r, c1), (r+1, c1))
	else:
	    # Assert same column, i.e. veritcal edge
	    assert n1[1] == n2[1]
	    assert abs(n1[0]-n2[0]) == 1
	    c = n1[1]
	    r1 = max(n1[0], n2[0])
	    return ((r1, c), (r1, c+1))

    def prnt(self):
	# Print row by row, first printing the regular row, then the cell row.
	for ri in range(self.nrows):
	    pr = []
	    for ci in range(self.ncols-1):
		pr.append('.')
		if self.edgeExists((ri, ci), (ri, ci+1)):
		    pr.append('-')
		else:
		    pr.append(' ')
	    pr.append('.')
	    print ''.join(pr)
	    if ri != (self.nrows-1):
		cr = []
		for ci in range(self.ncols):
		    if self.edgeExists((ri, ci), (ri+1, ci)):
			cr.append('|')
		    else:
			cr.append(' ')
		    if ci != (self.ncols-1):
			if (ri+1, ci+1) in self.interestingCells:
			    ct = self.getCount((ri+1, ci+1))
			    cr.append(str(ct))
			else:
			    cr.append(' ')
		print ''.join(cr)

def test1():
    p = Puzzle(4, 5)
    p.setCount((1, 1), 2)
    p.addEdge((0, 0), (0, 1))
    p.addEdge((0, 0), (1, 0))
    try:
	p.addEdge((1, 1), (1, 0))  # should raise exception
	assert False
    except CellCapExceeded: pass

test1()

def test_neighbors():
    p = Puzzle(4, 5)
    nrs = p.neighbors((0, 0))
    assert len(nrs) == 2
    nrs = p.neighbors((1, 2))
    assert len(nrs) == 4

test_neighbors()


test_puzzle_easy = '''
 202 
2   2
2  23
    2
 2 23'''

CELL_COUNTS = '0123'

def parse(inp):
    cellCountsMatrix = []
    current_row = []
    for c in inp:
	if c == '\n':
	    if current_row:
		cellCountsMatrix.append(current_row)
		current_row = []
	elif c in CELL_COUNTS:
	    current_row.append(int(c))
	elif c == ' ':
	    current_row.append(4)
    if current_row: cellCountsMatrix.append(current_row)

    # Check that all rows have the same count
    row_length = None
    for r in cellCountsMatrix:
	if row_length is None:
	    row_length = len(r)
	else:
	    if row_length != len(r):
		print "Unequal row lengths (non-rectangular puzzle) in %s" % inp
		assert False
    p = Puzzle(len(cellCountsMatrix)+1, len(cellCountsMatrix[0])+1)
    for ri, r in enumerate(cellCountsMatrix):
	for ci, c in enumerate(r):
	    if c != 4:
		p.setCount((ri+1, ci+1), c)
    p.freezePuzzle()
    return p

def test2():
    p = parse(test_puzzle_easy)
    assert p.interestingCells is not None
    assert p.getCount((1, 1)) == 4
    assert p.getCount((2, 1)) == 2
test2()

def test_adjacent_veritical():
    p = parse('33')
    ac = p.getAdjacentCells((0, 1), (1, 1))
    assert len(ac) == 2
    assert ac[0] == (1, 1)
    assert ac[1] == (1, 2)

test_adjacent_veritical()

def test_vertical_edge_neighbors1():
    p = parse('33')
    assert p.nrows == 2
    assert p.ncols == 3
    p.addEdge((0, 1), (1, 1))
    assert p.getCount((1, 1)) == 2
    assert p.getCount((1, 2)) == 2

test_vertical_edge_neighbors1()

def test_vertical_edge_neighbors2():
    p = parse('22\n22')
    assert p.nrows == 3
    assert p.ncols == 3
    p.addEdge((0, 1), (1, 1))
    assert p.getCount((1, 1)) == 1
    assert p.getCount((1, 2)) == 1
    p.removeEdge((0, 1), (1, 1))
    assert p.getCount((1, 1)) == 2
    assert p.getCount((1, 2)) == 2

test_vertical_edge_neighbors2()

class Solved(BaseException): pass

def search_solve(p, start):
    for n in p.neighbors(start):
	try:
	    p.addEdge(start, n)
	except: continue
	if p.degree(n) == 2 and p.isSolved():
	    print '+++++++'
	    p.prnt()
	    raise Solved()
	if False and random.random() > 0.99:
	    clear_screen()
	    print '======='
	    p.prnt()
	    sys.stdout.flush()
	    time.sleep(0.1)
	search_solve(p, n)
	p.removeEdge(start, n)

def clear_screen():
    print(chr(27) + "[2J")

test_puzzle_easy_2 = '''
0233 
 21 1
31   
31   
 2 1 '''
def test_search_solve_easy_2():
    try:
	search_solve(parse(test_puzzle_easy_2), (0, 1))
	search_solve(parse(test_puzzle_easy_2), (0, 2))
	search_solve(parse(test_puzzle_easy_2), (1, 1))
    except Solved: pass
    else:
	assert False
# test_puzzle_easy_2()

def starting_points(p):
    start_list = []
    for k,v in p.cellCounts.viewitems():
	assert v != 4
	if len(start_list) == 0 or len(start_list) > (5 - v):
	    r, c = k
	    start_list = [(r, c), (r-1, c), (r, c-1), (r-1, c-1)]
	    start_list = random.sample(start_list, 5-v)
    assert start_list
    return start_list

def solve(p):
    try:
	for s in starting_points(p):
	    search_solve(p, s)
    except Solved: pass
    else:
	print "Could not solve puzzle"

def test_complete_solve_easy_2():
    solve(parse(test_puzzle_easy_2))

test_complete_solve_easy_2()
