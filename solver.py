# todo here make the map loader and the maze solver

# todo mss 'SOLVE' knop maken

# /// +/- 722 lines code

import pygame as py
import sys, time, os

from scripts.tilemap import Tilemap

# /// if working with 2 monitors, enable this:
# os.environ['SDL_VIDEO_WINDOW_POS'] = '-1650,100'

class Solver:
    def __init__(self):

        self.size = (1000, 800)
        self.FPS = 5
        self.bg_color = (200, 200, 200)

        self.screen = py.display.set_mode(self.size)
        self.clock = py.time.Clock()

        self.tiles = {
            'start': (0, 255, 0),
            'wall': (0, 0, 0),
            'end': (255, 0, 0),
            'reachable': (100, 0, 175),
            'check': (255,255,0),
            'final': (0,0,255)
        }
        self.tile_types = list(self.tiles.keys())

        self.tilemap = Tilemap(self)


        # self.maze_load_file = 'full_screen.json'
        self.maze_load_file = 'full_screen.json'
        try:
            self.tilemap.load('mazes/' + self.maze_load_file)
        except FileNotFoundError:
            print('Map not found, creating new map')
            pass


    def run(self):
        py.init()

        while True:
            self.screen.fill(self.bg_color)

            self.tilemap.solver_update()
            self.tilemap.draw(self.screen, False)

            self.check_events()

            py.display.update()
            self.clock.tick(self.FPS)

    def solve(self):
        #  /// average time: 10.8 minutes
        # self.tilemap.solve_v1(False)

        # /// average time: 0,03 seconds
        self.tilemap.solve_v2(True)

    def check_events(self):
        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                sys.exit()
            
            if event.type == py.KEYDOWN:
                if event.key == py.K_s:
                    start_time = time.time()
                    self.solve()
                    end_time = time.time()
                    print(f"Solving took {end_time - start_time} seconds")
                if event.key == py.K_a:

                    times = []
                    for i in range(10):
                        print(f'({i}/10) done')
                        start_time = time.time()
                        self.solve()
                        end_time = time.time()

                        times.append(end_time - start_time)
                        self.tilemap.load('mazes/' + self.maze_load_file)

                    average = sum(times) / len(times)
                    print(f"Solving with v1 took an average of: {average} seconds")

                    # print(f"Solving took {end_time - start_time} seconds")
                if event.key == py.K_ESCAPE:
                    self.tilemap.load('mazes/' + self.maze_load_file)

Solver().run()