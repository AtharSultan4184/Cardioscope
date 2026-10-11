"""
place_arteries.py - design LAD / LCX / RCA centre-lines on the baked heart and verify them visually.

Each waypoint is [mode, a, b]; the third coordinate is looked up on the outermost surface
(modes: cut / back / L / R - see outer())
Output: src/config/arteryPaths.json   (read by the web viewer)   +  overlay PNG for checking.
These paths are SCHEMATIC (hand-placed from anatomy textbooks' general course), not patient anatomy.
"""
import sys, json
sys.path.insert(0, 'tools')
import numpy as np, matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from viewlib import draw_mesh, draw_path, draw_path_occluded

d = np.load(sys.argv[1]); pos, nrm, tris = d['pos'], d['nrm'], d['idx']
CUT_Z = pos[:, 2].max() + 0.25          # just in front of the open face of this cut-away model
LIFT = 0.20                             # distance the centre-line floats above the surface (cm)
RAD = 0.6                               # neighbourhood used to look up the outer surface (cm)

def outer(mode, a, b):
    """Return a 3D point on the OUTERMOST surface along one axis. Waypoint modes:
       cut  (x, y): on the open front face            back (x, y): posterior surface (min z)
       L    (y, z): left border (max x)               R    (y, z): right border (min x)"""
    if mode == 'cut':
        return np.array([a, b, CUT_Z])
    if mode == 'back':
        m = (abs(pos[:, 0] - a) < RAD) & (abs(pos[:, 1] - b) < RAD); assert m.any(), (mode, a, b)
        return np.array([a, b, pos[m, 2].min() - LIFT])
    if mode == 'L':
        m = (abs(pos[:, 1] - a) < RAD) & (abs(pos[:, 2] - b) < RAD); assert m.any(), (mode, a, b)
        return np.array([pos[m, 0].max() + LIFT, a, b])
    if mode == 'R':
        m = (abs(pos[:, 1] - a) < RAD) & (abs(pos[:, 2] - b) < RAD); assert m.any(), (mode, a, b)
        return np.array([pos[m, 0].min() - LIFT, a, b])
    raise ValueError(mode)

ARTERIES = json.load(open(sys.argv[2]))
out = {}
for name, spec in ARTERIES.items():
    pts = [outer(mode, a, b) for mode, a, b in spec['waypoints']]
    out[name] = {'label': spec['label'], 'description': spec['description'],
                 'points': [[round(float(c), 3) for c in p] for p in pts]}
json.dump({'cutPlaneZ': round(float(CUT_Z), 3), 'arteries': out}, open(sys.argv[3], 'w'), indent=2)

fig, ax = plt.subplots(2, 2, figsize=(15, 15)); cols = {'LAD': '#00e5ff', 'LCX': '#ffe600', 'RCA': '#39ff14'}
for a, v in zip(ax.ravel(), ['front', 'back', 'left', 'right']):
    draw_mesh(a, pos, tris, v, tint=(0.55, 0.35, 0.35))
    for name, s in out.items():
        P = np.array(s['points']); tck, _ = splprep(P.T, s=0, k=min(3, len(P) - 1)); Q = np.array(splev(np.linspace(0, 1, 120), tck)).T
        draw_path_occluded(a, Q, v, pos, cols.get(name, 'w'), lw=3)
plt.tight_layout(); plt.savefig(sys.argv[4], dpi=60)
print('ok', {k: len(v['points']) for k, v in out.items()})
