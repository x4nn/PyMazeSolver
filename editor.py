# todo here make the map maker and saver

# /// place: 'left click'
# /// delete: 'right click'
# /// delete all: 'r', 
# /// change tile: 'scroll'
# /// grid: 'g'
# /// save: 's'
# /// fill paths: 'f'
# /// unfill paths: 'u'

# /// time 10 tries and choose quickest, save routes and time in object in array and then itterate for fastest routeor shortest route, maybe map out the illegal routes if possible

import pygame as py
import sys

from scripts.tilemap import Tilemap

class Editor:
    def __init__(self):

        self.size = (1000, 800)
        self.FPS = 60
        self.bg_color = (200, 200, 200)

        self.screen = py.display.set_mode(self.size)
        self.clock = py.time.Clock()

        self.tiles = {
            'start': (0, 255, 0),
            'wall': (0, 0, 0),
            'end': (255, 0, 0),
            # 'reachable': (173, 216, 230),
            'path': self.bg_color #(255, 255, 255) # de solver weet niet dat de witte tiles het path zijn want deze info staat niet bij zijn tile info
        }

        self.tilemap = Tilemap(self)

        self.maze_file = 'full_screen.json'
        self.maze_save_file = 'full_screen.json'
        try:
            self.tilemap.load('mazes/' + self.maze_file)
        except FileNotFoundError:
            print('Map not found, creating new map')
            pass

        self.clicking = False
        self.right_clicking = False

        self.tile_types = list(self.tiles.keys())
        self.holding_tile = 1
        self.grid = True

    def run(self):
        py.init()

        while True:
            self.screen.fill((255, 255, 0))

            mpos = py.mouse.get_pos()
            grid_x = (mpos[0] // self.tilemap.tile_size) * self.tilemap.tile_size
            grid_y = (mpos[1] // self.tilemap.tile_size) * self.tilemap.tile_size

            self.tilemap.editor_update(self.clicking, self.right_clicking, self.holding_tile, mpos)
            self.tilemap.draw(self.screen, self.grid)

            py.draw.rect(self.screen, self.tiles[self.tile_types[self.holding_tile]], (grid_x, grid_y, self.tilemap.tile_size, self.tilemap.tile_size))

            self.check_events()

            py.display.update()
            self.clock.tick(self.FPS)

    def check_events(self):
        for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    sys.exit()

                if event.type == py.KEYDOWN:
                    if event.key == py.K_r:
                        self.tilemap.tilemap = {}
                    if event.key == py.K_s:
                        self.tilemap.save('mazes/' + self.maze_save_file)
                    if event.key == py.K_g:
                        self.grid = not self.grid
                    if event.key == py.K_f:
                        self.tilemap.fill_paths()
                    if event.key == py.K_u:
                        self.tilemap.unfill_paths()

                if event.type == py.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                    if event.button == 3:
                        self.right_clicking = True
                    if event.button == 4:
                        self.holding_tile = (self.holding_tile - 1) % len(self.tile_types)
                    if event.button == 5:
                        self.holding_tile = (self.holding_tile + 1) % len(self.tile_types)
                
                if event.type == py.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False                           

Editor().run()