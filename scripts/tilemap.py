import pygame as py
import json, sys, time, random

class Tilemap:
    def __init__(self, editor, tile_size=50):
        self.editor = editor
        self.tile_size = tile_size

        self.grid_color = (123, 45, 201)
        self.tilemap = {}
        self.start_pos = None
        self.end_pos = None

        self.possible_tiles = []

    def editor_update(self, clicking, right_clicking, holding_tile, mpos):
        if clicking:
            self.add_tile(holding_tile, mpos)
        if right_clicking:
            self.remove_tile(mpos)

    def solver_update(self):
        pass

    def draw(self, surf, grid=True):
        if grid:
            self.draw_grid()

        for cord in self.tilemap:
            color = self.tilemap[cord]['color']
            cord = self.tilemap[cord]['pos']
            py.draw.rect(surf, color, (cord[0], cord[1], self.tile_size, self.tile_size))

    def tuple_format_cord(self, cord):
        x, y = map(int, cord.split(';'))
        return tuple((x, y))

    def draw_grid(self):
        rows = self.editor.screen.get_height() // self.tile_size
        cols = self.editor.screen.get_width() // self.tile_size

        for i in range(rows):
            for j in range(cols):
                py.draw.rect(self.editor.screen, self.grid_color, (j * self.tile_size, i * self.tile_size, self.tile_size, self.tile_size), 1)

    def add_tile(self, holding_tile, mpos):
        pos = self.get_grid_pos(mpos)
        tile = {'type': self.editor.tile_types[holding_tile], 'color': self.editor.tiles[self.editor.tile_types[holding_tile]], 'pos': tuple(self.tuple_format_cord(pos))}

        if self.check_start_end(tile)[0]: # returns True if already exists
            self.remove_tile(self.tuple_format_cord(self.check_start_end(tile)[1]))

        self.tilemap[pos] = tile

    def check_start_end(self, tile):
        type = tile['type']

        if type == 'start':
            for key in self.tilemap.keys():
                if self.tilemap[key]['type'] == 'start':
                    return True, key
        elif type == 'end':
            for key in self.tilemap.keys():
                if self.tilemap[key]['type'] == 'end':
                    return True, key
        
        return False, None

    def remove_tile(self, loc):
        pos = self.get_grid_pos(loc)

        if pos in self.tilemap:
            del self.tilemap[pos]

    def get_grid_pos(self, mpos):
        x = (mpos[0] // self.tile_size) * self.tile_size
        y = (mpos[1] // self.tile_size) * self.tile_size

        return str(x) + ';' + str(y)
    
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        data = json.load(f)
        f.close()

        self.tilemap = data['tilemap']
        self.tile_size = data['tile_size']

        for tile in self.tilemap:
            if self.tilemap[tile]['type'] == 'start':
                self.start_pos = self.tilemap[tile]['pos']
            elif self.tilemap[tile]['type'] == 'end':
                self.end_pos = self.tilemap[tile]['pos']

    def fill_paths(self):
        rows = self.editor.screen.get_height() // self.tile_size
        cols = self.editor.screen.get_width() // self.tile_size

        for i in range(rows):
            for j in range(cols):
                cord = str(j * self.tile_size) + ';' + str(i * self.tile_size)
                if cord not in self.tilemap:
                    cord_above = str(j * self.tile_size) + ';' + str(max(0, i * self.tile_size - self.tile_size))
                    cord_left = str(max(0, j * self.tile_size - self.tile_size)) + ';' + str(i * self.tile_size)
                    cord_below = str(j * self.tile_size) + ';' + str(min(rows * self.tile_size, i * self.tile_size + self.tile_size))
                    cord_right = str(min(cols * self.tile_size, j * self.tile_size + self.tile_size)) + ';' + str(i * self.tile_size)

                    if self.is_path_tile(cord_above, cord_left, cord_right, cord_below):
                        self.tilemap[cord] = {'type': 'path', 'color': self.editor.tiles['path'], 'pos': self.tuple_format_cord(cord)}

    def unfill_paths(self):
        rows = self.editor.screen.get_height() // self.tile_size
        cols = self.editor.screen.get_width() // self.tile_size

        for i in range(rows):
            for j in range(cols):
                cord = str(j * self.tile_size) + ';' + str(i * self.tile_size)
                if cord in self.tilemap and self.tilemap[cord]['type'] == 'path':
                    del self.tilemap[cord]

    def is_path_tile(self, n1, n2, n3, n4):
        neighbors = 0

        if n1 in self.tilemap:
            neighbors += 1
        if n2 in self.tilemap:
            neighbors += 1
        if n3 in self.tilemap:
            neighbors += 1
        if n4 in self.tilemap:
            neighbors += 1

        return neighbors >= 2

    # /// Hij checked ALLE tiles, als er meerdere oplossingen zijn en hij heeft 'alle' routes (tiles) gechecked, 
    # /// toont hij de kortste route die die heeft gevonden. Hij zal altijd een weg vinden maar voor grote mazes 
    # /// is dit zeer traag
    def solve_v1(self, show):
        print('v1')
        start_tile = self.tilemap[str(self.start_pos[0]) + ';' + str(self.start_pos[1])]
        current_tile = start_tile

        junctions = []
        unchecked_tiles = []
        processed_tiles = []
        dead_ends = []
        reached_end = False

        unchecked_tiles.append(start_tile)
        junctions.append(start_tile)

        while len(unchecked_tiles) != 0 and reached_end == False:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    sys.exit()

            current_tile = unchecked_tiles[0]

            if self.count_neighbors(current_tile) > 2:
                junctions.append(current_tile)

            if self.count_neighbors(current_tile) == 1:
                dead_ends.append(current_tile)

            for neighbor in self.get_neighbors(current_tile):
                if neighbor['type'] == 'end':
                    reached_end = True
                    break
                if neighbor not in processed_tiles and neighbor not in unchecked_tiles and neighbor['type'] != 'wall':
                    neighbor['color'] = self.editor.tiles['reachable']
                    neighbor['junction'] = junctions[max(0, len(junctions)-1)]['pos']
                    unchecked_tiles.append(neighbor)
            
            processed_tiles.append(current_tile)
            unchecked_tiles.pop(0)
            
            self.show_path(show) # ///

        dead_ends = self.add_loos_ends(dead_ends, unchecked_tiles)
        self.traceback(junctions, dead_ends, processed_tiles, show)

        self.left_over_tiles()

        self.find_shortest(show)

    def traceback(self, junctions, dead_ends, previous_processed_tiles, show=False):
        # print('traceback')
        while len(dead_ends) > 0:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    sys.exit()

            not_at_junction = True
            start_tile = dead_ends[0]

            processed_tiles = []
            unchecked_tiles = []
            unchecked_tiles.append(start_tile)
            processed_tiles.append(start_tile)

            while not_at_junction:
                current_tile = unchecked_tiles[0]

                if current_tile in junctions:
                    not_at_junction = False
                else:
                    current_tile['color'] = self.editor.bg_color

                    for neighbour in self.get_neighbors(current_tile):
                        if neighbour not in processed_tiles and neighbour in previous_processed_tiles and neighbour['type'] != 'wall':
                            unchecked_tiles.append(neighbour)
                            unchecked_tiles.pop(0)

                processed_tiles.append(current_tile)

                self.show_path(show) # ///

            dead_ends.pop(0)

    def find_shortest(self, show):
        # print('finding shortest, may take a while...')
        routes = []

        color = (255,255,0)

        loop = True

        route_counter = 0 # counts amount of checked routes
        while loop:
            route = []
            start_tile = self.tilemap[str(self.start_pos[0]) + ';' + str(self.start_pos[1])]
            current_tile = start_tile
            not_dead = True
            while not_dead:
                for event in py.event.get():
                    if event.type == py.QUIT:
                        py.quit()
                        sys.exit()
                
                route.append(current_tile)
                current_tile['checked'] = True
                current_tile['color'] = color

                if current_tile['type'] == 'end': # wanneer geen reachable neigbors ook dead
                    route.append(current_tile)
                    not_dead = False

                if len(self.get_reachable_neighbors(current_tile)) > 0:
                    current_tile = random.choice(self.get_reachable_neighbors(current_tile))
                else:
                    not_dead = False

                self.show_path(show) # ///

                route_counter += 1

            self.remove_tmp_path()
            routes.append(route)

            # end_tile = self.tilemap[str(self.end_pos[0]) + ';' + str(self.end_pos[1])]
            # if end_tile in route:
            #     loop = False

            if self.all_routes_checked():
                loop = False

        best_route = self.eliminate_false_routes(routes)

        print('routes tested', route_counter)

        if show:
            self.mark_final_path(best_route)

    def mark_final_path(self, route):
        for tile in self.tilemap:
            if self.tilemap[tile] not in route and self.tilemap[tile]['type'] != 'wall':
                self.tilemap[tile]['color'] = self.editor.bg_color

        for tile in route:
            tile['color'] = self.editor.bg_color

        for tile in route:
            tile['color'] = self.editor.tiles['final']

            time.sleep(0.01)
            self.editor.screen.fill(self.editor.bg_color)
            self.draw(self.editor.screen, False)
            py.display.update()

        for tile in self.tilemap:
            if self.tilemap[tile]['type'] == 'start':
                self.tilemap[tile]['color'] = self.editor.tiles['start']
            elif self.tilemap[tile]['type'] == 'end':
                self.tilemap[tile]['color'] = self.editor.tiles['end']
            
    def eliminate_false_routes(self, routes):
        end_tile = self.tilemap[str(self.end_pos[0]) + ';' + str(self.end_pos[1])]
        
        end_routes = []

        for route in routes:
            if end_tile in route:
                end_routes.append(route)

        fastest_route = end_routes[0]
        for route in end_routes:
            if len(route) < len(fastest_route):
                fastest_route = route

        return fastest_route

    def remove_tmp_path(self):
        for tile in self.possible_tiles:
            if tile['type'] == 'start':
                tile['color'] = self.editor.tiles['start']
            elif tile['type'] == 'end':
                tile['color'] = self.editor.tiles['end']
            else:
                tile['color'] = self.editor.tiles['reachable']

    def all_routes_checked(self):
        # Check if there are no reachable colors left, return true
        for tile in self.tilemap:
            if self.tilemap[tile].get('checked', True) == False:
                return False
        return True

    def get_reachable_neighbors(self, tile):
        neighbors = []
        for neighbor in self.get_neighbors(tile):
            if neighbor['color'] == self.editor.tiles['reachable'] or neighbor['type'] == 'end':
                neighbors.append(neighbor)
        return neighbors

    def left_over_tiles(self):
        for tile in self.tilemap:
            if self.tilemap[tile]['color'] == self.editor.tiles['reachable'] or self.tilemap[tile]['type'] == 'end' or self.tilemap[tile]['type'] == 'start':
                self.tilemap[tile]['checked'] = False
                self.possible_tiles.append(self.tilemap[tile])

    def add_loos_ends(self, dead_ends, unchecked_tiles):
        updated_dead_ends = dead_ends.copy()

        for tile in unchecked_tiles:
            updated_dead_ends.append(tile)

        return updated_dead_ends

    def count_neighbors(self, tile):
        pos = tile['pos']
        count = 0

        if self.tilemap[str(pos[0]) + ';' + str(pos[1] - self.tile_size)]['type'] != 'wall':
            count += 1
        if self.tilemap[str(pos[0] + self.tile_size) + ';' + str(pos[1])]['type'] != 'wall':
            count += 1
        if self.tilemap[str(pos[0]) + ';' + str(pos[1] + self.tile_size)]['type'] != 'wall':
            count += 1
        if self.tilemap[str(pos[0] - self.tile_size) + ';' + str(pos[1])]['type'] != 'wall':
            count += 1
        
        return count
    
    def count_path_neighbors(self, tile):
        pos = tile['pos']
        count = 0

        if self.tilemap[str(pos[0]) + ';' + str(pos[1] - self.tile_size)]['type'] not in ['wall', 'reachable']:
            count += 1
        if self.tilemap[str(pos[0] + self.tile_size) + ';' + str(pos[1])]['type'] not in ['wall', 'reachable']:
            count += 1
        if self.tilemap[str(pos[0]) + ';' + str(pos[1] + self.tile_size)]['type'] not in ['wall', 'reachable']:
            count += 1
        if self.tilemap[str(pos[0] - self.tile_size) + ';' + str(pos[1])]['type'] not in ['wall', 'reachable']:
            count += 1
        
        return count

    def get_neighbors(self, tile):
        pos = tile['pos']

        return [
            self.tilemap[str(pos[0]) + ';' + str(pos[1] - self.tile_size)], # boven 
            self.tilemap[str(pos[0] + self.tile_size) + ';' + str(pos[1])], # rechts
            self.tilemap[str(pos[0]) + ';' + str(pos[1] + self.tile_size)], # onder
            self.tilemap[str(pos[0] - self.tile_size) + ';' + str(pos[1])]  # links
            ]
    
    # /// rules:
    # ///  1: no loops in maze
    # ///  2: no splitsings next to each other 
    def solve_v2(self, show):
        print('v2')
        junctions = self.mark_junctions()
        
        start_tile = self.tilemap[str(self.start_pos[0]) + ';' + str(self.start_pos[1])]
        cur_tile = start_tile

        processed = []
        new_juncs = []

        color = self.editor.tiles['check']
        tmp_counter = 0

        not_found = True
        while not_found:

            loop = True
            while loop:
                for event in py.event.get():
                    if event.type == py.QUIT:
                        py.quit()
                        sys.exit()

                cur_tile['color'] = color
                neighbors = self.get_neighbors(cur_tile)
                processed.append(cur_tile)

                if self.count_neighbors(cur_tile) == 1 and cur_tile['type'] != 'start':
                    loop = False
                    self.show_path(show) # ///
                    # time.sleep(0.5) # ///
                    self.back_to_junc(cur_tile, new_juncs[len(new_juncs) - 1], color, show)
                    cur_tile = new_juncs[len(new_juncs) - 1]
                    break
                    
                tile_found = False
                for tile in neighbors:
                    if tile['type'] != 'wall' and tile not in processed:

                        if tile in junctions:
                            tile['color'] = color
                            cur_tile['checked'] = [True, True]
                            new_juncs.append(tile)
                            processed.append(tile)
                            loop = False

                        cur_tile = tile
                        tile_found = True

                
                if tile_found == False:
                    tmp_counter += 1
                    if tmp_counter % 2 == 0:
                        self.back_to_junc(new_juncs[len(new_juncs) - 1], new_juncs[len(new_juncs) - 2], color, show)
                        new_juncs.pop(len(new_juncs) - 1)
                    cur_tile = new_juncs[len(new_juncs) - 1]
                    break

                if cur_tile['type'] == 'end':
                    not_found = False
                    break

                self.show_path(show) # ///

            self.show_path(show) # ///

            for tile in self.get_neighbors(cur_tile): # dit is een junction
                if tile['type'] != 'wall' and tile not in processed:
                    cur_tile = tile
                    tile['checked'][0] = True

        self.mark_start()
    
    def mark_junctions(self):
        junctions = []
        for tile in self.tilemap:
            if self.tilemap[tile]['type'] != 'wall':
                cur_tile = self.tilemap[tile]
                neighbors = self.count_neighbors(cur_tile)

                cur_tile['checked'] = [False, False]

                if neighbors > 2:
                    junctions.append(cur_tile)
                    cur_tile['junction'] = True
                else:
                    cur_tile['junction'] = False

        return junctions
    
    def back_to_junc(self, dead_end, junction, color, show):
        cur_tile = dead_end
        processed = []

        while cur_tile != junction:
            for event in py.event.get():
                    if event.type == py.QUIT:
                        py.quit()
                        sys.exit()

            cur_tile['color'] = self.editor.bg_color
            neighbors = self.get_neighbors(cur_tile)
            processed.append(cur_tile)

            for neighbor in neighbors:
                if neighbor['type'] != 'wall' and neighbor not in processed and neighbor['color'] == color: 
                    cur_tile = neighbor
                if neighbor == junction:
                    cur_tile = neighbor
                    break

            self.show_path(show) # ///

    def mark_start(self):
        self.tilemap[str(self.start_pos[0]) + ';' + str(self.start_pos[1])]['color'] = self.editor.tiles['start']

    def show_path(self, show):
        if show:
            time.sleep(0.005)
            self.editor.screen.fill(self.editor.bg_color)
            self.draw(self.editor.screen, False)
            py.display.update()