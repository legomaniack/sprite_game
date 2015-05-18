#from pprint import pprint
from random import randint
from itertools import combinations

def pprint(matrix):
	s = [[str(e) for e in row] for row in matrix]
	lens = [max(map(len, col)) for col in zip(*s)]
	fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
	table = [fmt.format(*row) for row in s]
	print ("\n".join(table))

WIDTH = 20
HEIGHT = 20

key = [
	"*", 	# Wall
	"."		# Floor
]
	
class Grid:
	def __init__(self, w, h):
		self.width = w
		self.height = h
		self.grid = []
		for r in range(h):
			self.grid.append(["*"]*w)
		self.rooms = []
	
	def gen(self):
		for i in range(1,4):
			gen = False
			i = 0
			while not gen:
				i+=1
				if i >= 15:
					gen = True
				t = randint(2,self.height-2)
				l = randint(2,self.width-2)
				w = randint(4,int(self.width/2))
				h = randint(4,int(self.height/2))
				if t+h >= self.height or l+w >= self.width:
					continue
				r = Room(t,l,w,h)
				inte = False
				for room in self.rooms:
					if r.intersects(room):
						inte = True
						break
				if inte:
					continue
				self.rooms.append(r)
				print("ok")
				r.apply(self.grid)
				gen = True
		for rc in combinations(self.rooms, 2):
			print("CHECK", rc[0], rc[1])
			if rc[0].intersects(rc[1], "vert"):
				c = randint(max(rc[0].left, rc[1].left),min(rc[0].right, rc[1].right)-1)
				fr = min(rc[0].bottom, rc[1].bottom)
				to = max(rc[0].top, rc[1].top)
				r = Room(fr, c, 1, to-fr)
				print(fr, to)
				print(r)
				r.apply(self.grid)
			if rc[0].intersects(rc[1], "horiz"):
				c = randint(max(rc[0].top, rc[1].top),min(rc[0].bottom, rc[1].bottom)-1)
				fr = min(rc[0].right, rc[1].right)
				to = max(rc[0].left, rc[1].left)
				print(fr, to)
				r = Room(c, fr, to-fr, 1)
				print(r)
				r.apply(self.grid)
		start_room = self.rooms[randint(0,len(self.rooms)-1)]
		rand_c = randint(start_room.left,start_room.right-1)
		rand_r = randint(start_room.top, start_room.bottom-1)
		self.start_sector = (rand_c,rand_r)
		pprint(self.grid)
			
				
		

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Room:
	def __init__(self, t, l, w, h):
		self.top = t
		self.left = l
		self.width = w
		self.height = h
		self.bottom = t+h
		self.right = l+w
	
	def contains(self, point):
		if (point.x >= self.left and point.x < self.right) and (point.y >= self.top and point.y < self.bottom):
			return True
		return False 
	
	def intersects(self, room, typ="both"):
		if typ == "both" or typ == "vert":
			if self.right <= room.left:
				return False
			if self.left >= room.right:
				return False
		if typ == "both" or typ == "horiz":
			if self.bottom <= room.top:
				return False
			if self.top >= room.bottom:
				return False
		return True
	
	def apply(self, grid, label="."):
		for r in range(len(grid)):
			for c in range(len(grid[r])):
				p = Point(r,c)
				if self.contains(p):
					grid[r][c] = label
	
	def __repr__(self):
		return "{!s} x {!s} Room from ({!s},{!s}) to ({!s},{!s})".format(self.width, self.height, self.left, self.top, self. right, self.bottom)
				
if __name__ == "__main__":	
	g = Grid(WIDTH, HEIGHT)
	g.gen()
	pprint(g.grid)

