import json
import matplotlib.pyplot as plt
from pathlib import Path

p = Path(__file__).parent / 'results.json'
if not p.exists():
    raise SystemExit(f"results.json not found at {p}")

with open(p, 'r') as f:
    data = json.load(f)

# Build arrays keyed by sum of capacities
cases = []
for case in data:
    caps = [int(x) for x in case['capacities']]
    s = sum(caps)
    bfs = case.get('bfs', {})
    dfs = case.get('dfs', {})
    cases.append({
        'name': case.get('name',''),
        'sum': s,
        'bfs_time': bfs.get('time'),
        'bfs_b': bfs.get('b'),
        'bfs_D': bfs.get('D'),
        'bfs_d': bfs.get('d'),
        'dfs_time': dfs.get('time'),
        'dfs_b': dfs.get('b'),
        'dfs_D': dfs.get('D'),
        'dfs_d': dfs.get('d'),
    })

cases.sort(key=lambda c: c['sum'])
xs = [c['sum'] for c in cases]

# Helper to plot
def make_plot(alg):
    if alg == 'bfs':
        bs = [c['bfs_b'] for c in cases]
        depths = [c['bfs_d'] for c in cases]
        times = [c['bfs_time'] for c in cases]
        title = 'BFS: branching factor b and shallowest solution depth d'
        fname = 'bfs_plot.png'
    else:
        bs = [c['dfs_b'] for c in cases]
        depths = [c['dfs_D'] for c in cases]
        times = [c['dfs_time'] for c in cases]
        title = 'DFS: branching factor b and maximum depth D'
        fname = 'dfs_plot.png'

    fig, ax1 = plt.subplots(figsize=(8,5))
    ax1.plot(xs, bs, '-o', label='avg branching (b)')
    ax1.plot(xs, depths, '-s', label=('d' if alg=='bfs' else 'D'))
    ax1.set_xlabel('Sum of capacities')
    ax1.set_ylabel('b / depth')
    ax1.legend(loc='upper left')
    ax1.grid(True, which='both', linestyle='--', alpha=0.4)

    ax2 = ax1.twinx()
    ax2.plot(xs, times, 'k--', label='time (s)')
    ax2.set_ylabel('time (s)')
    ax2.legend(loc='upper right')

    plt.title(title)
    out = Path(__file__).parent / fname
    plt.tight_layout()
    plt.savefig(out)
    print(f"Saved plot to: {out}")
    plt.close()

make_plot('bfs')
make_plot('dfs')
