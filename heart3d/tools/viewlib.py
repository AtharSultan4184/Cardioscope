"""Tiny orthographic software renderer (matplotlib) used ONLY to design/verify artery paths offline."""
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

VIEWS = {  # name: (direction camera looks along)
    'front': np.array([0, 0, -1.0]), 'back': np.array([0, 0, 1.0]),
    'left':  np.array([-1.0, 0, 0]), 'right': np.array([1.0, 0, 0])}

def basis(name):
    d = VIEWS[name]; up = np.array([0, 1.0, 0]); right = np.cross(d, up); return d, right, up

def draw_mesh(ax, pos, tris, name, tint=(0.85, 0.3, 0.3)):
    d, r, u = basis(name)
    T = pos[tris]; n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    depth = -(T.mean(1) @ d)                     # larger = nearer camera? painter: far first
    order = np.argsort(-(T.mean(1) @ d))[::-1]   # far (high d-dot... ) handled below
    order = np.argsort(T.mean(1) @ -d)           # smallest "toward camera" first -> far first
    sx = T @ r; sy = T @ u
    polys = np.stack([sx, sy], -1)[order]
    sh = np.clip(np.abs(n @ d), 0.2, 1)[order]
    cols = np.stack([sh * tint[0], sh * tint[1], sh * tint[2], np.ones_like(sh)], 1)
    ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors='none'))
    ax.set_aspect('equal'); ax.set_xlim(-10, 10); ax.set_ylim(-10, 10)
    ax.set_xticks(range(-10, 11, 2)); ax.set_yticks(range(-10, 11, 2)); ax.grid(True, alpha=.35, lw=.5); ax.set_title(name)

def draw_path(ax, pts, name, color, lw=3, label=None, dots=True):
    d, r, u = basis(name); pts = np.asarray(pts)
    ax.plot(pts @ r, pts @ u, '-', color=color, lw=lw, solid_capstyle='round')
    if dots: ax.plot(pts @ r, pts @ u, 'o', color='white', mec='k', ms=4)


from scipy.spatial import cKDTree
def visible_mask(P, pos, name, tol=0.7, rad=0.30):
    """True where a point on the centre-line is NOT hidden behind the mesh in this view."""
    d, r, u = basis(name)
    tree = cKDTree(np.c_[pos @ r, pos @ u]); depth = pos @ d
    vis = np.ones(len(P), bool)
    for i, p in enumerate(P):
        idx = tree.query_ball_point([p @ r, p @ u], rad)
        if idx and depth[idx].min() < (p @ d) - tol: vis[i] = False
    return vis

def draw_path_occluded(ax, P, name, pos, color, lw=3):
    d, r, u = basis(name); vis = visible_mask(P, pos, name)
    x, y = P @ r, P @ u
    for i in range(len(P) - 1):
        ok = vis[i] and vis[i + 1]
        ax.plot(x[i:i + 2], y[i:i + 2], '-' if ok else ':', color=color, lw=lw if ok else 1, alpha=1 if ok else .45)
