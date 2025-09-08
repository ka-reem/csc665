#!/usr/bin/env python3
"""
Maze generator + BFS visualization

Controls:
 - SPACE : start/pause BFS search
 - R     : regenerate maze
 - +/-   : increase/decrease animation delay
 - ESC/Q : quit

Requires: pygame
"""
import random
import collections
import pygame
import sys
import time

# Configuration
CELL_SIZE = 12  # pixels per cell
MAZE_W = 51     # must be odd
MAZE_H = 41     # must be odd
BORDER = 1

# Colors
COLOR_BG = (30, 30, 30)
COLOR_WALL = (10, 10, 10)
COLOR_OPEN = (230, 230, 230)
COLOR_VISITED = (100, 160, 255)
COLOR_FRONTIER = (80, 200, 120)
COLOR_PATH = (255, 220, 80)
COLOR_START = (200, 60, 60)
COLOR_GOAL = (200, 60, 60)

FPS = 60


def generate_maze(w, h):
    """Generate a maze using randomized DFS (recursive backtracker).
    Maze grid: 1=wall, 0=open. w and h should be odd.
    """
    assert w % 2 == 1 and h % 2 == 1, "width and height must be odd"
    grid = [[1 for _ in range(w)] for _ in range(h)]

    start = (1, 1)
    grid[start[1]][start[0]] = 0
    stack = [start]

    dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < w - 1 and 1 <= ny < h - 1:
                if grid[ny][nx] == 1:
                    neighbors.append((nx, ny))
        if neighbors:
            nx, ny = random.choice(neighbors)
            # carve between
            bx, by = (x + nx) // 2, (y + ny) // 2
            grid[by][bx] = 0
            grid[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    return grid


def neighbors4(x, y, w, h):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            yield nx, ny


def bfs_search(grid, start, goal):
    """Generator that yields the BFS state step-by-step for visualization.
    Yields tuples: (current, frontier_set, visited_set, prev_dict)
    When finished, returns prev_dict for path reconstruction.
    """
    w = len(grid[0])
    h = len(grid)
    q = collections.deque()
    q.append(start)
    visited = set([start])
    prev = {start: None}

    while q:
        current = q.popleft()
        # yield state
        yield current, set(q), set(visited), dict(prev)
        if current == goal:
            break
        cx, cy = current
        for nx, ny in neighbors4(cx, cy, w, h):
            if grid[ny][nx] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                prev[(nx, ny)] = (cx, cy)
                q.append((nx, ny))
                # yield after enqueue so frontier updates visually
                yield current, set(q), set(visited), dict(prev)
    # final yield
    yield current, set(q), set(visited), dict(prev)
    return prev


def reconstruct_path(prev, start, goal):
    if goal not in prev:
        return []
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path


class MazeVisualizer:
    def __init__(self, grid):
        self.grid = grid
        self.h = len(grid)
        self.w = len(grid[0])
        self.cell_size = CELL_SIZE
        self.width = self.w * self.cell_size
        self.height = self.h * self.cell_size

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("BFS Maze Search")
        self.clock = pygame.time.Clock()

        self.start = (1, 1)
        self.goal = (self.w - 2, self.h - 2)

        self.search_gen = None
        self.current = None
        self.frontier = set()
        self.visited = set()
        self.prev = {}
        self.path = []

        self.running_search = False
        self.delay = 0.01  # seconds between steps

    def draw_cell(self, x, y, color):
        rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, color, rect)

    def draw(self):
        self.screen.fill(COLOR_BG)
        # draw maze
        for y in range(self.h):
            for x in range(self.w):
                if self.grid[y][x] == 1:
                    self.draw_cell(x, y, COLOR_WALL)
                else:
                    self.draw_cell(x, y, COLOR_OPEN)
        # visited
        for (x, y) in self.visited:
            self.draw_cell(x, y, COLOR_VISITED)
        # frontier
        for (x, y) in self.frontier:
            self.draw_cell(x, y, COLOR_FRONTIER)
        # path
        for (x, y) in self.path:
            self.draw_cell(x, y, COLOR_PATH)
        # start and goal
        self.draw_cell(self.start[0], self.start[1], COLOR_START)
        self.draw_cell(self.goal[0], self.goal[1], COLOR_GOAL)

        pygame.display.flip()

    def start_search(self):
        self.search_gen = bfs_search(self.grid, self.start, self.goal)
        self.running_search = True
        # prime the generator
        try:
            s = next(self.search_gen)
            self.current, self.frontier, self.visited, self.prev = s
        except StopIteration:
            self.running_search = False

    def step_search(self):
        if not self.search_gen:
            return
        try:
            s = next(self.search_gen)
            self.current, self.frontier, self.visited, self.prev = s
            # if reached goal, reconstruct path
            if self.current == self.goal:
                self.path = reconstruct_path(self.prev, self.start, self.goal)
                self.running_search = False
        except StopIteration:
            # finished
            self.running_search = False
            self.path = reconstruct_path(self.prev, self.start, self.goal)

    def run(self):
        last_step = 0.0
        while True:
            now = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit(0)
                    if event.key == pygame.K_SPACE:
                        if not self.running_search:
                            # start or restart search
                            self.path = []
                            self.start_search()
                        else:
                            # pause
                            self.running_search = False
                    if event.key == pygame.K_r:
                        # regenerate maze
                        self.grid = generate_maze(self.w, self.h)
                        self.visited = set()
                        self.frontier = set()
                        self.prev = {}
                        self.path = []
                        self.search_gen = None
                        self.running_search = False
                    if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.delay = max(0.0, self.delay - 0.005)
                    if event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                        self.delay = min(1.0, self.delay + 0.005)

            if self.running_search and (now - last_step) >= self.delay:
                self.step_search()
                last_step = now

            # always update frontier/visited to current state when paused
            self.draw()
            self.clock.tick(FPS)


def main():
    grid = generate_maze(MAZE_W, MAZE_H)
    viz = MazeVisualizer(grid)
    viz.run()


if __name__ == '__main__':
    main()