# ============================================================
# 3 Jugs problem (or n jugs) definition
# Authors: S. El Alaoui and ChatGPT 5
# ============================================================

class SearchProblem:
    def start_state(self):
        raise NotImplementedError()

    def actions(self, state):
        raise NotImplementedError()

    def cost(self, state, action):
        raise NotImplementedError()

    def succ(self, state, action):
        raise NotImplementedError()

    def is_end(self, state):
        raise NotImplementedError()


# Action = of type Tuple[str, int, Optional[int]]  # ('fill', i, None) | ('empty', i, None) | ('pour', i, j)
# State = of type Tuple[int, ...] 


class NJugsProblem(SearchProblem):
    """
    N-jugs problem with the standard operations:
      - fill(i): fill jug i to its capacity from an infinite source
      - empty(i): empty jug i to drain
      - pour(i, j): pour from jug i into jug j until i is empty or j is full

    State is an N-tuple of amounts (non-negative ints).
    Cost per action defaults to 1 (can be changed with cost_per_move).
    """

    def __init__(self, capacities, goal):
        caps = tuple(int(c) for c in capacities)
        if any(c <= 0 for c in caps):
            raise ValueError("All capacities must be positive integers.")


        if not goal:
            raise ValueError("Goal must be provided.")

        goal = tuple(int(x) for x in goal)
        if len(goal) != len(capacities):
            raise ValueError("Goal length must match number of capacities (", len(capacities), ").")

        self.capacities = caps
        self.n = len(caps)
        self._goal = tuple(goal)

    # ---- SearchProblem API ----
    def start_state(self):
        return tuple(0 for _ in range(self.n))

    def is_end(self, state):
        return state == self._goal

    def cost(self, state, action) -> int:
        # Unit cost per move by default 1.
        return 1

    """
    Returns the set of all possible actions available on the current state of the jugs.

    The actions function should return a list of all the possible actions that can be taken given a state.

    Each action should be represented as a tuple (action_kind, i, j) 
    action_kind is one of: "fill", "empty" and "pour"
    i corresponds to the jug affected by the action
    j is a valid number only if the action is "pour" (i.e. pour from jug i into jug j). Otherwise it should be set to None
    """
    def actions(self, state):
        """
        Return a list of valid actions for the given state.

        Each action is a tuple (kind, i, j) where kind is one of
        'fill', 'empty', 'pour'. For 'fill' and 'empty' j is None.
        For 'pour', i is source index and j is destination index.
        """
        if state is None:
            return []

        actions = []
        # fill and empty actions
        for i in range(self.n):
            if state[i] < self.capacities[i]:
                actions.append(("fill", i, None))
            if state[i] > 0:
                actions.append(("empty", i, None))

        # pour actions between distinct jugs
        for i in range(self.n):
            if state[i] == 0:
                continue
            for j in range(self.n):
                if i == j:
                    continue
                if state[j] < self.capacities[j]:
                    actions.append(("pour", i, j))

        return actions

    # NOTE (Part 3 - instrumentation hint):
    # The return value of `actions(state)` is the local branching factor at `state`.
    # To compute the average branching factor b across the search you can:
    #  - when expanding a state in a search algorithm, call `problem.actions(state)` and
    #    accumulate its length into `total_child_count` and increment `nodes_expanded` by 1.
    #  - after the search finishes, b = total_child_count / nodes_expanded (avoid div by zero).
    # This keeps the search model-agnostic: all solvers can reuse the same metric by calling
    # `actions()` each time they expand a node.

    """
    Returns the state of the jugs after taking action (kind, i, j), without modifying the original state.

    If `action` is not a valid action for the current state, you  should raise an exception.

    The returned state should be: tuple([j1, j2, j3]) 
    where j1, j2 and j3 represent the amount of water in each jug, respectively. 

    Importantly, the original state should be left unmodified. This 
    means that simply updating the input state itself is not a correct 
    implementation of this function. You’ll likely want to make a 
    copy of the state first before making any changes.
    """
    def succ(self, state, action):
        """
        Return the new state after applying `action` to `state`.

        Raises an exception if the action is invalid for the given state.
        """
        if not isinstance(action, tuple) or len(action) != 3:
            raise ValueError("Action must be a tuple (kind, i, j)")

        kind, i, j = action

        # basic validation of indices
        if not (isinstance(i, int) and 0 <= i < self.n):
            raise IndexError("Invalid jug index i: {}".format(i))
        if j is not None and not (isinstance(j, int) and 0 <= j < self.n):
            raise IndexError("Invalid jug index j: {}".format(j))

        # copy state to mutable list
        ns = list(state)

        if kind == "fill":
            # must be allowed: current amount < capacity
            if ns[i] >= self.capacities[i]:
                raise ValueError("Cannot fill jug {}: already full".format(i))
            ns[i] = self.capacities[i]
            return tuple(ns)

        if kind == "empty":
            if ns[i] == 0:
                raise ValueError("Cannot empty jug {}: already empty".format(i))
            ns[i] = 0
            return tuple(ns)

        if kind == "pour":
            if j is None:
                raise ValueError("Pour action requires destination index j")
            if i == j:
                raise ValueError("Cannot pour a jug into itself")
            if ns[i] == 0:
                raise ValueError("Cannot pour from empty jug {}".format(i))
            if ns[j] >= self.capacities[j]:
                raise ValueError("Cannot pour into full jug {}".format(j))

            space = self.capacities[j] - ns[j]
            transfer = min(ns[i], space)
            ns[i] -= transfer
            ns[j] += transfer
            return tuple(ns)

        raise ValueError("Unknown action kind: {}".format(kind))


    # ---- Helpers ----

    @property
    def goal(self):
        return self._goal

    @property
    def capacities_tuple(self):
        return self.capacities

