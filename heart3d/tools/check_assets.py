"""Validates public/models/human_heart.glb and src/config/arteryPaths.json.  Usage: python tools/check_assets.py"""
import json, struct, io, math, sys
import numpy as np
from PIL import Image

GLB, PATHS = 'public/models/human_heart.glb', 'src/config/arteryPaths.json'
b = open(GLB, 'rb').read()
magic, ver, total = struct.unpack('<4sII', b[:12]); assert magic == b'glTF' and ver == 2 and total == len(b), 'bad GLB header/length'
jl, jt = struct.unpack('<I4s', b[12:20]); assert jt == b'JSON' and jl % 4 == 0
j = json.loads(b[20:20 + jl]); o = 20 + jl
bl, bt = struct.unpack('<I4s', b[o:o + 8]); assert bt == b'BIN\x00' and bl % 4 == 0 and o + 8 + bl == len(b)
bin_ = b[o + 8:]; assert j['buffers'][0]['byteLength'] == len(bin_)
for i, v in enumerate(j['bufferViews']):
    assert v['byteOffset'] % 4 == 0 and v['byteOffset'] + v['byteLength'] <= len(bin_), f'bufferView {i} out of range'
view = lambda i: bin_[j['bufferViews'][i]['byteOffset']:][:j['bufferViews'][i]['byteLength']]
pos = np.frombuffer(view(0), '<f4').reshape(-1, 3); idx = np.frombuffer(view(3), '<u2')
assert np.isfinite(pos).all() and idx.max() < len(pos) and len(idx) % 3 == 0
assert np.allclose(pos.min(0), j['accessors'][0]['min'], atol=1e-4) and np.allclose(pos.max(0), j['accessors'][0]['max'], atol=1e-4)
for k in (4, 5): Image.open(io.BytesIO(view(k))).load()
assert 'KHR_materials_pbrSpecularGlossiness' not in json.dumps(j), 'deprecated extension present'
print(f'GLB ok: {len(pos)} vertices, {len(idx)//3} triangles, {total/1e6:.2f} MB; bounds {pos.min(0).round(2)} .. {pos.max(0).round(2)}')

d = json.load(open(PATHS)); lo, hi = pos.min(0) - 1.0, pos.max(0) + 1.0
for name in ('LAD', 'LCX', 'RCA'):
    P = np.array(d['arteries'][name]['points']); assert P.shape[1] == 3 and len(P) >= 4 and np.isfinite(P).all(), name
    assert (P >= lo).all() and (P <= hi).all(), f'{name} has points outside the heart bounding box'
    print(f'{name}: {len(P)} points, length ~{np.linalg.norm(np.diff(P, axis=0), axis=1).sum():.1f} cm - inside heart bounds')
print('ALL ASSET CHECKS PASSED')
