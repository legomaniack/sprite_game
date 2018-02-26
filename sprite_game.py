#TODO: http://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame

#INIT -------------------------

FPS = 30

DEBUG = True

WIN_HEIGHT = 800
WIN_WIDTH = 800
SPRITE_SIZE = 24

import pygame, sys, configparser, math
from pygame.locals import *
from random import randint
import gen_map
#from pprint import pprint

def pprint(matrix):
	s = [[str(e) for e in row] for row in matrix]
	lens = [max(map(len, col)) for col in zip(*s)]
	fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
	table = [fmt.format(*row) for row in s]
	print ('\n'.join(table))

pygame.init()

test_sprite = pygame.Surface((SPRITE_SIZE,SPRITE_SIZE))
test_sprite.fill((0,0,255))
test_sprite2 = pygame.Surface((SPRITE_SIZE,SPRITE_SIZE))
test_sprite2.fill((0,255,255))


config = configparser.ConfigParser()

def debug(msg, typ ='m'):
    if typ == 'm':
        print("    Message: " + msg)
    elif typ == 'w':
        print("    Warning: " + msg)
    elif typ == 'e':
        print("    ERROR: " + msg)
    else:
        print("    {0!s}: " + msg).format(typ)


#EVENTS & EVENT HANDLERS ------

class Event:
    def __init__(self):
        self.name = "Undefined Event"

class TickEvent(Event):
    def __init__(self):
        self.name = "CPU Tick Event"

class QuitEvent(Event):
    def __init__(self):
        self.name = "Program Quit Event"

class KeyPressEvent(Event):
    def __init__(self, key):
        self.name = "Key Press Event: {0!s}".format(key)
        self.key = key

class DrawMapEvent(Event):
    def __init__(self, file):
        self.name = "Initialize Map Event"
        self.file = file

class MapDrawnEvent(Event):
    def __init__(self, map_):
        self.name = "Map Initialized Event"
        self.map_ = map_

class GameStartEvent(Event):
    def __init__(self):
        self.name = "Game Started Event"

class CharactorMoveRequest(Event):
    def __init__(self, direction):
        self.name = "Charactor Move Request"
        self.direction = direction

class CharactorMoveEvent(Event):
    def __init__(self, charactor, direction):
        self.name = "Charactor Move Event"
        self.charactor = charactor
        self.direction = direction

class CharactorPlaceEvent(Event):
    def __init__(self, charactor):
        self.name = "Charactor Place Event"
        self.charactor = charactor

class CharactorSpriteEvent(Event):
    def __init__(self, charactor, file):
        self.name = "Charactor Sprite Event"
        self.charactor = charactor
        self.file = file

class SpriteMoveEvent(Event):
    def __init__(self, charactor):
        self.name = "Sprite Move Event"
        self.charactor = charactor


###

class EventManager:
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.eventQueue = []

    def register_listener(self, listener):
        self.listeners[ listener ] = 1

    def unregister_listener(self, listener):
        if listener in self.listeners:
            del self.listeners[ listener ]

    def post(self, event):
        if not isinstance(event, TickEvent) and DEBUG:
            debug(event.name)
        for listener in self.listeners:
            listener.notify(event)



#CONTROLLER --------------------

class KeyboardController:
    """Handles input from keyboard"""
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)

    def notify(self, event):
        if isinstance(event, TickEvent):
            for event in pygame.event.get():
                ev = None
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    ev = QuitEvent()

                elif event.type == KEYDOWN and (event.key == K_w):
                    ev = CharactorMoveRequest(1)

                elif event.type == KEYDOWN and (event.key == K_a):
                    ev = CharactorMoveRequest(3)

                elif event.type == KEYDOWN and (event.key == K_s):
                    ev = CharactorMoveRequest(6)

                elif event.type == KEYDOWN and (event.key == K_d):
                    ev = CharactorMoveRequest(4)

                elif event.type == KEYDOWN:
                    ev = KeyPressEvent(event.key)


                if ev:
                    self.event_manager.post(ev)


class CPUSpinnerController:
    """Runs a 'while' loop to generate 'TickEvent's.
    Also handles (cpu) frame rate"""
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)

        self.keep_going = 1
        self.fps_clock = pygame.time.Clock()

    def run(self):
        while self.keep_going:
            event = TickEvent()
            self.event_manager.post(event)

            self.fps_clock.tick(FPS)

    def notify(self, event):
        if isinstance(event, QuitEvent):
            self.keep_going = False

#VIEW -------------------------

class PygameView:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.sprites = {}

        self.screen = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
        self.camera = None #To use the camera, .update() on rect to follow, then use .apply(rect) instead of rect
        self.game_map = None

    def draw_map(self):
        self.screen.fill(self.game_map.background_color)
        for r in range(len(self.game_map.sectors)):
            for c in range(len(self.game_map.sectors[r])):
                self.screen.blit(self.game_map.sectors[r][c].sprite, (c*SPRITE_SIZE, r*SPRITE_SIZE))

    def update_sprites(self):
        for c in self.sprites:
            s = self.sprites[c]
            updates = s.update()
            if 'move' in updates:
                self.event_manager.post(SpriteMoveEvent(s.charactor))

    def draw_sprites(self):
        for c in self.sprites:
            s = self.sprites[c]
            self.screen.blit(s.sprite, s.get_rect())

    def draw_everything(self):
        self.draw_map()
        self.draw_sprites()
        pygame.display.flip()

    def test_tiles(self):
        for r in range(len(self.game_map.tiles)):
            for c in range(len(self.game_map.tiles[r])):
                self.screen.blit(self.game_map.tiles[r][c], (c*SPRITE_SIZE, r*SPRITE_SIZE))
        pygame.display.flip()

    def get_sprite(self, charactor):
        return self.sprites[id(charactor)]

    def notify(self, event):
        if isinstance(event, TickEvent):
            #self.test_tiles()
            self.draw_everything()
            self.update_sprites()
        if isinstance(event, CharactorMoveEvent):
            self.get_sprite(event.charactor).moving = True
            self.get_sprite(event.charactor).direction = event.direction
        if isinstance(event, MapDrawnEvent):
            self.game_map = event.map_
            self.camera = Camera(basic_camera, self.game_map.width, self.game_map.height)
        if isinstance(event, CharactorSpriteEvent):
            self.sprites[id(event.charactor)] = CharatorSprite(event.charactor)
            if event.file != None:
                self.get_sprite(self.charator).build(event.file)

class CharatorSprite:
    def __init__(self, charactor):
        self.charactor = charactor
        self.sprites = [] #2D array, seperated by direction, and then loop iteration
        self.moving = False
        self.counter = 0
        self.direction = 3
        self.sprite = test_sprite
        self.x = self.charactor.sector.pos[0] * SPRITE_SIZE
        self.y = self.charactor.sector.pos[1] * SPRITE_SIZE

    def update(self):
        update_events = []
        if not self.is_moved():
            #set sprite
            xdir, ydir = self.get_move_dir()
            self.x += xdir*4
            self.y += ydir*4
            self.counter += 1
        if self.moving and self.counter == 5:
            self.counter = 0
            self.x = self.charactor.sector.pos[0] * SPRITE_SIZE
            self.y = self.charactor.sector.pos[1] * SPRITE_SIZE
            update_events.append('move')
            self.moving = False
        return update_events

    def is_moved(self):
        return (self.x == self.charactor.sector.pos[0] * SPRITE_SIZE and self.y == self.charactor.sector.pos[1] * SPRITE_SIZE)

    def get_move_dir(self):
        xcng = (self.charactor.sector.pos[0] * SPRITE_SIZE) - self.x
        ycng = (self.charactor.sector.pos[1] * SPRITE_SIZE) - self.y
        if xcng != 0:
            xcng = math.copysign(1, xcng)
        if ycng != 0:
            ycng = math.copysign(1, ycng)
        return xcng, ycng

    def get_sector_rect(self):
        x = self.charactor.sector.pos[0] * SPRITE_SIZE
        y = self.charactor.sector.pos[1] * SPRITE_SIZE
        return pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, SPRITE_SIZE, SPRITE_SIZE)

    def load_spritesheet(self, file):
        self.spritesheet = pygame.image.load(file)
        self.sprites = []
        width = int(self.spritesheet.get_width()/SPRITE_SIZE)
        height = int(self.spritesheet.get_height()/SPRITE_SIZE)

        for row in range(height):
            self.sprites.append([])
            for col in range(width):
                self.sprites[row].append(self.spritesheet.subsurface((col*SPRITE_SIZE, row*SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE)))



class Camera:
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target_rect):
        return target_rect.move(self.state.topleft)

    def update(self, target_rect):
        self.state = self.camera_func(self.state, target_rect)

def basic_camera(camera, target_rect):
    HALF_WIDTH = int(WIN_WIDTH/2)
    HALF_HEIGHT = int(WIN_HEIGHT/2)
    l, t, _, _ = target_rect # l = left,  t = top
    _, _, w, h = camera      # w = width, h = height
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    HALF_WIDTH = int(WIN_WIDTH/2)
    HALF_HEIGHT = int(WIN_HEIGHT/2)
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h # center player

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-WIN_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-WIN_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top

    return Rect(l, t, w, h)


#MODEL ------------------------

class Game:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.map = Map(event_manager)
        self.player = Charactor(event_manager)
        self.started = False

    def start(self):
        self.event_manager.post(DrawMapEvent('test.map'))
        self.player.build()
        self.event_manager.post(GameStartEvent())
        self.started = True

    def notify(self, event):
        pass

#MAP

class Map:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.sectors = []
        self.start_sector = None
        self.background_color = None

    def notify(self, event):
        if isinstance(event, DrawMapEvent):
            self.load_map(event.file)

    def load_spritesheet(self, file):
        self.spritesheet = pygame.image.load(file)
        self.tiles = []
        width = int(self.spritesheet.get_width()/SPRITE_SIZE)
        height = int(self.spritesheet.get_height()/SPRITE_SIZE)

        for row in range(height):
            self.tiles.append([])
            for col in range(width):
                self.tiles[row].append(self.spritesheet.subsurface((col*SPRITE_SIZE, row*SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE)))

    def load_map(self, file):
        map_reader = configparser.ConfigParser()
        debug("Loading map file '{0!s}'".format(file))
        try:
            map_reader.read(file)
        except:
            debug("Could not read map file '{0!s}'. Exiting.".format(file), 'e')
            event_manager.post(QuitEvent())
        debug("Loading spritesheet '{0!s}'".format(map_reader['level']['tileset']))
        self.load_spritesheet(map_reader['level']['tileset'])
        #debug("Parsing map file")
        #self.layout = map_reader['level']['map'].split("\n")
        map_grid = gen_map.Grid(20, 20)
        map_grid.gen()
        self.layout = map_grid.grid
        debug("Map loaded: ")
        pprint(self.layout)
        self.background_color = pygame.Color(map_reader['level']['background color'])

        debug("Building map")
        self.sectors = []
        self.width = len(self.layout[0])
        self.height = len(self.layout)
        for r in range(len(self.layout)):
            self.sectors.append([])
            for c in range(len(self.layout[r])):
                new_sector = Sector(map_reader[self.layout[r][c]]['type'], map_reader.getboolean(self.layout[r][c],'walkable'), (c,r))
                self.sectors[r].append(new_sector)
        pprint(self.sectors)
        s_s = map_grid.start_sector
        self.start_sector = self.sectors[int(s_s[0])][int(s_s[1])]


        debug("Building list of neighbors")
        self.calc_neighbors()
        debug("Calculating sector sprites")
        self.calc_map_sprites()

        ev = MapDrawnEvent(self)
        self.event_manager.post(ev)

    def get_tile(self, r, c):
        if r >= 0 and r < len(self.sectors):
            if c >= 0 and c < len(self.sectors[r]):
                return self.sectors[r][c]
        return None

    def calc_neighbors(self):                       #012
        for r in range(len(self.sectors)):          #3 4
            for c in range(len(self.sectors[r])):   #567
                s = self.sectors[r][c]
                n = s.neighbors
                n[0] = self.get_tile(r-1,c-1)
                n[1] = self.get_tile(r-1,c)
                n[2] = self.get_tile(r-1,c+1)
                n[3] = self.get_tile(r,c-1)
                n[4] = self.get_tile(r,c+1)
                n[5] = self.get_tile(r+1,c-1)
                n[6] = self.get_tile(r+1,c)
                n[7] = self.get_tile(r+1,c+1)
                bi = ""
                for t in n:
                    if t == None or t.sprite_type == 'wall':
                        bi = '1'+bi
                    else:
                        bi = '0'+bi
                bi = '0b'+bi
                s.arrangement = int(bi, 2)

                bio = ""
                for i in (1,3,4,6):
                    t = n[i]
                    if t == None or t.sprite_type == 'wall':
                        bio = '1'+bio
                    else:
                        bio = '0'+bio
                bio = '0b'+bio
                s.ortho = int(bio, 2)

                bid = ""
                for i in (0,2,5,7):
                    t = n[i]
                    if t == None or t.sprite_type == 'wall':
                        bid = '1'+bid
                    else:
                        bid = '0'+bid
                bid = '0b'+bid
                s.diag = int(bid, 2)

    def get_random_sprite(self, *s):
        return s[randint(0, len(s)-1)]

    def get_alt_sprite(self, primary, *s):
        if randint(0, 3) == 0:
            return s[randint(0, len(s)-1)]
        return primary

    def calc_map_sprites(self):
        for r in range(len(self.sectors)):
            for c in range(len(self.sectors[r])):
                s = self.sectors[r][c]
                n = s.neighbors     #        1      1 2
                t = self.tiles      #       2 4
                p = s.sprite        #        8      4 8
                if s.sprite_type == "floor":
                    if s.ortho == 0:
                        p = self.get_random_sprite(t[1][1],t[1][2],t[2][1],t[2][2])
                    elif s.ortho == 15:
                        p = t[1][1]

                    #Adjacent to wall
                    elif s.ortho == 1:
                        p = t[0][1]
                    elif s.ortho == 2:
                        p = t[2][0]
                    elif s.ortho == 4:
                        p = t[2][3]
                    elif s.ortho == 8:
                        p = t[3][1]

                    #Corner
                    elif s.ortho == 3:
                        p = t[0][0]
                    elif s.ortho == 5:
                        p = t[0][3]
                    elif s.ortho == 10:
                        p = t[3][0]
                    elif s.ortho == 12:
                        p = t[3][3]

                    #Hallway
                    elif s.ortho in (9, 13, 11):
                        p = t[4][0]
                    elif s.ortho in (6, 14, 7):
                        p = t[4][1]


                elif s.sprite_type == "wall":
                    #Background Wall & Inner corner
                    if s.ortho == 15:
                        if s.diag == 15:
                            p = self.get_random_sprite(t[6][1],t[6][2],t[7][1],t[7][2])
                        elif s.diag in (0, 3, 10, 12, 5, 1, 2, 4, 8, 6, 9):
                            debug("Invalid wall arrangement at pos [r{0!s}, c{1!s}]: Using fallback sprite".format(r,c), 'e')
                            p = t[4][3] #MUST MAKE CUSTOM SPRITE OR INVALIDATE SINGLE WALLS
                        elif s.diag == 7:
                            p = t[9][0]
                        elif s.diag == 11:
                            p = t[9][2]
                        elif s.diag == 13:
                            p = t[11][0]
                        elif s.diag == 14:
                            p = t[11][2]

                    #Freestanding Wall
                    elif s.ortho == 0:
                        p = t[12][3]

                    #Wall Strips
                    elif s.ortho == 1:
                        p = t[11][3]
                    elif s.ortho == 2:
                        p = t[12][2]
                    elif s.ortho == 4:
                        p = t[12][0]
                    elif s.ortho == 8:
                        p = t[9][3]
                    elif s.ortho == 9:
                        p = t[10][3]
                    elif s.ortho == 6:
                        p = t[12][1]

                    #Corners
                    elif s.ortho == 3:
                        p = t[8][3]
                    elif s.ortho == 5:
                        p = t[8][0]
                    elif s.ortho == 12:
                        p = t[5][0]
                    elif s.ortho == 10:
                        p = t[5][3]

                    #Flat Walls
                    elif s.ortho == 7:
                        p = self.get_alt_sprite(t[8][1], t[8][2])
                    elif s.ortho == 13:
                        p = self.get_alt_sprite(t[6][0], t[7][0])
                    elif s.ortho == 11:
                        p = self.get_alt_sprite(t[6][3], t[7][3])
                    elif s.ortho == 14:
                        p = self.get_alt_sprite(t[5][1], t[5][2])

                else:
                    p = t[4][3]

                s.sprite = p


class Sector:
    def __init__(self, s_t, w, pos):
        self.sprite_type = s_t
        self.pos = pos
        self.sprite = None
        self.walkable = w
        self.arrangement = 0
        self.ortho = 0
        self.diag = 0
        self.neighbors = [None]*8   # 012
                                    # 3 4
                                    # 567

    def move_possible_to(self, direction):
        return self.neighbors[direction].walkable

    def __repr__(self):
        return self.sprite_type

#CHARACTOR
class Charactor:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.done_moving = True
        self.sector = None

    def move(self, direction):
        if self.sector.move_possible_to(direction) and self.done_moving:
            self.sector = self.sector.neighbors[direction]
            self.done_moving = False

            self.event_manager.post(CharactorMoveEvent(self, direction))

    def place(self, sector):
        self.sector = sector

        self.event_manager.post(CharactorPlaceEvent(self))

    def build(self, file=None):
        self.event_manager.post(CharactorSpriteEvent(self, file))

    def notify(self, event):
        if isinstance(event, MapDrawnEvent):
            game_map = event.map_
            self.place(game_map.start_sector)
        if isinstance(event, CharactorMoveRequest):
            self.move(event.direction)
        if isinstance(event, SpriteMoveEvent):
            if event.charactor == self:
                self.done_moving = True





#MAIN -------------------------

def main():
    event_manager = EventManager()

    keybd = KeyboardController(event_manager)
    spinner = CPUSpinnerController(event_manager)
    pyview = PygameView(event_manager)
    game = Game(event_manager)

    game.start()
    spinner.run()

    #Game has Exited
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
