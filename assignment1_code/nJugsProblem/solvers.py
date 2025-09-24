# ============================================================
# Solvers — Backtracking (two different implementations)
#           Placeholder for BFS, DFS
# Authors: S. El Alaoui and ChatGPT 5
# ============================================================

import math
from collections import deque
import time

from the3jugs import *

"""
Depth-first backtracking with simple 'explored' pruning.
Stores the best (lowest-cost) path of states encountered to any goal.
This is a recursive implementation. 

returns a dictionary with the following informatin: 
    best_cost= path cost (i.e. number of steps from start to the goal),
    best_path= [s_0, ..., s*],
    found= boolean : path found or not 
    expanded= # of state explored 
        
"""
class BacktrackingSearch:
    def __init__(self, problem: SearchProblem):
        self.best_cost = math.inf
        self.best_path = None
        self.explored = set()
        self.problem = problem

    def recurse(self, state, path, cost: int):
        if self.problem.is_end(state):
       
            if cost < self.best_cost:
                self.best_cost = cost
                self.best_path = path[:]  # copy
                # print(self.best_cost)
            return

        for action in self.problem.actions(state):
            next_state = self.problem.succ(state, action)
            key = str(next_state)
            # key = next_state
            if key not in self.explored:
                
                self.explored.add(key)
                
                self.recurse(next_state, path + [next_state], cost + self.problem.cost(state, action))

    def solve(self):
        start = self.problem.start_state()
        self.explored.add(str(start))
        self.recurse(start, [], 0)
        return dict(
            best_cost=self.best_cost,
            best_path=[self.problem.start_state()] + (self.best_path or []),
            found=(self.best_path is not None),
            expanded=len(self.explored),
        )

    # NOTE (Part 3 - instrumentation guidance):
    # If you extend this class to collect the metrics required in Part 3,
    # consider recording the following while searching:
    #  - total_child_count: sum of number of successor actions generated (for average branching b)
    #  - nodes_expanded: number of distinct states expanded (same as 'expanded' above)
    #  - max_depth_seen: maximum path depth reached during recursion (D)
    #  - shallowest_solution_depth: when is_end is True, record len(path) and keep the minimum (d)
    #  - elapsed time: use time.time() at entry/exit of solve()
    # Implementation hint: pass current depth as an int param when recursing and update max/solution depths.

"""
Depth-first backtracking with simple 'explored' pruning (iterative).
Stores the best (lowest-cost) path of states encountered to any goal.
This is an iterative implementation. 

returns a dictionary with the following informatin: 
    best_cost= path cost (i.e. number of steps from start to the goal),
    best_path= [s_0, ..., s*],
    found= boolean : path found or not 
    expanded= # of state explored

"""
class BacktrackingSearchIterative:
    def __init__(self, problem):
        self.best_cost = math.inf
        self.best_path = None
        self.explored = set()
        self.problem = problem

    def solve(self):
        start = self.problem.start_state()
        start_key = str(start)
        self.explored.add(start_key)

        # Stack holds tuples: (state, path_from_after_start, cost_so_far)
        stack = [(start, [], 0)]

        while stack:
            state, path, cost = stack.pop()

            # Goal check
            if self.problem.is_end(state):
                if cost < self.best_cost:
                    self.best_cost = cost
                    self.best_path = path[:]  # copy
                continue

            # Expand
            actions = list(self.problem.actions(state))
            # To match recursive DFS order, push in reverse so first action is explored first.
            for action in reversed(actions):
                next_state = self.problem.succ(state, action)
                key = str(next_state)
                if key not in self.explored:
                    self.explored.add(key)
                    next_cost = cost + self.problem.cost(state, action)
                    stack.append((next_state, path + [next_state], next_cost))

        return dict(
            best_cost=self.best_cost,
            best_path=[self.problem.start_state()] + (self.best_path or []),
            found=(self.best_path is not None),
            expanded=len(self.explored),
        )


"""
Add an iterative implementation of DFS.
BFS explores nodes level by leveland is guaranteed to find a goal at minimum depth (the fewest steps).

returns a dictionary with the following informatin: 
    best_cost= path cost (i.e. number of steps from start to the goal),
    best_path= [s_0, ..., s*],
    found= boolean : path found or not 
    expanded= # of state explored
"""
class BFSSearch:
    def __init__(self, problem: SearchProblem):
        self.problem = problem

    def solve(self):
        start = self.problem.start_state()
        start_key = str(start)

        # Metrics for Part 3
        t0 = time.time()
        total_child_count = 0
        nodes_expanded = 0
        max_depth_seen = 0
        shallowest_solution_depth = None

        queue = deque()
        queue.append((start, []))  # state, path-from-after-start

        explored = set()
        explored.add(start_key)

        while queue:
            state, path = queue.popleft()
            depth = len(path)
            nodes_expanded += 1
            if depth > max_depth_seen:
                max_depth_seen = depth

            if self.problem.is_end(state):
                d = len(path)
                shallowest_solution_depth = d if shallowest_solution_depth is None else min(shallowest_solution_depth, d)
                elapsed = time.time() - t0
                b = (total_child_count / nodes_expanded) if nodes_expanded > 0 else 0.0
                return dict(
                    best_cost=len(path),
                    best_path=[self.problem.start_state()] + path,
                    found=True,
                    expanded=len(explored),
                    time=elapsed,
                    b=b,
                    D=max_depth_seen,
                    d=shallowest_solution_depth,
                )

            actions = list(self.problem.actions(state))
            total_child_count += len(actions)
            for action in actions:
                next_state = self.problem.succ(state, action)
                key = str(next_state)
                if key not in explored:
                    explored.add(key)
                    queue.append((next_state, path + [next_state]))

        elapsed = time.time() - t0
        b = (total_child_count / nodes_expanded) if nodes_expanded > 0 else 0.0
        return dict(
            best_cost=float('nan'),
            best_path=[],
            found=False,
            expanded=len(explored),
            time=elapsed,
            b=b,
            D=max_depth_seen,
            d=shallowest_solution_depth,
        )

"""
Add an iterative implementation of DFS.
DFS explores along a path as deep as possible before backtracking 
and returns the first solution found, which may not be the shortest.

returns a dictionary with the following informatin: 
    best_cost= path cost (i.e. number of steps from start to the goal),
    best_path= [s_0, ..., s*],
    found= boolean : path found or not 
    expanded= # of state explored
"""
class DFSSearch:


    def __init__(self, problem: SearchProblem):
        self.problem = problem

    def solve(self):
        start = self.problem.start_state()
        start_key = str(start)

        # Metrics for Part 3
        t0 = time.time()
        total_child_count = 0
        nodes_expanded = 0
        max_depth_seen = 0
        shallowest_solution_depth = None

        stack = [(start, [])]  # state, path-from-after-start
        explored = set()
        explored.add(start_key)

        while stack:
            state, path = stack.pop()
            depth = len(path)
            nodes_expanded += 1
            if depth > max_depth_seen:
                max_depth_seen = depth

            if self.problem.is_end(state):
                d = len(path)
                shallowest_solution_depth = d if shallowest_solution_depth is None else min(shallowest_solution_depth, d)
                elapsed = time.time() - t0
                b = (total_child_count / nodes_expanded) if nodes_expanded > 0 else 0.0
                return dict(
                    best_cost=len(path),
                    best_path=[self.problem.start_state()] + path,
                    found=True,
                    expanded=len(explored),
                    time=elapsed,
                    b=b,
                    D=max_depth_seen,
                    d=shallowest_solution_depth,
                )

            # To mimic recursive DFS order, iterate actions in reverse when pushing
            actions = list(self.problem.actions(state))
            total_child_count += len(actions)
            for action in reversed(actions):
                next_state = self.problem.succ(state, action)
                key = str(next_state)
                if key not in explored:
                    explored.add(key)
                    stack.append((next_state, path + [next_state]))

        elapsed = time.time() - t0
        b = (total_child_count / nodes_expanded) if nodes_expanded > 0 else 0.0
        return dict(
            best_cost=float('nan'),
            best_path=[],
            found=False,
            expanded=len(explored),
            time=elapsed,
            b=b,
            D=max_depth_seen,
            d=shallowest_solution_depth,
        )



