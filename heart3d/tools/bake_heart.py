"""
bake_heart.py  -  turn the downloaded Sketchfab GLB into a light, static GLB.

WHY: the original file is a *skinned* mesh under a node scaled 0.01 and uses the
deprecated KHR_materials_pbrSpecularGlossiness extension. Three.js may render that at
the wrong size / without textures, and our artery tubes could not be aligned reliably.
This script:
  1. computes the rest-pose vertex positions the glTF spec prescribes (skinning at t=0),
  2. re-centres the model and scales it so 1 unit ~ 1 cm,
  3. writes a plain GLB with a standard metallic-roughness material,
  4. downsizes the textures (diffuse 2048 px, normal 1024 px, JPEG).

Source model: "Human_heart_3d_model" by marxtrax  https://skfb.ly/oDKZq  (CC BY 4.0)
Usage:  python tools/bake_heart.py <source.glb> <textures_dir> <out.glb>
"""
import json, struct, sys, io
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation as R

src, tex_dir, out_path = sys.argv[1:4]
f = open(src, 'rb').read()
clen, _ = struct.unpack('<I4s', f[12:20]); j = json.loads(f[20:20 + clen])
off = 20 + clen; blen, _ = struct.unpack('<I4s', f[off:off + 8]); bin_ = f[off + 8:off + 8 + blen]

def acc(i):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]
    n = {'VEC3': 3, 'VEC2': 2, 'VEC4': 4, 'SCALAR': 1, 'MAT4': 16}[a['type']]
    dt = {5126: '<f4', 5123: '<u2', 5125: '<u4', 5121: 'u1'}[a['componentType']]
    s = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(bin_, dtype=dt, count=a['count'] * n, offset=s).reshape(a['count'], n)

# ---- node hierarchy -> joint world matrices (rest pose) --------------------------------
N = j['nodes']; parent = {}
for i, n in enumerate(N):
    for c in n.get('children', []): parent[c] = i
def local(i):
    n = N[i]
    S = np.diag(list(n.get('scale', [1, 1, 1])) + [1])
    Rm = np.eye(4); Rm[:3, :3] = R.from_quat(n.get('rotation', [0, 0, 0, 1])).as_matrix()
    T = np.eye(4); T[:3, 3] = n.get('translation', [0, 0, 0])
    return T @ Rm @ S
def world(i):
    M = local(i)
    while i in parent: i = parent[i]; M = local(i) @ M
    return M

sk = j['skins'][0]
ibm = acc(sk['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)   # col-major -> row-major
jm = np.stack([world(k) @ ibm[idx] for idx, k in enumerate(sk['joints'])])
prim = j['meshes'][0]['primitives'][0]; at = prim['attributes']
P = acc(at['POSITION']); NRM = acc(at['NORMAL']); UV = acc(at['TEXCOORD_0'])
J = acc(at['JOINTS_0']).astype(int); W = acc(at['WEIGHTS_0']).astype(float)
I = acc(prim['indices']).reshape(-1).astype(np.uint32)
Ph = np.c_[P, np.ones(len(P))]
pos = np.zeros((len(P), 3))
for k in range(4):
    pos += W[:, k:k + 1] * np.einsum('nij,nj->ni', jm[J[:, k]], Ph)[:, :3]

pos *= 100.0                                   # metres -> centimetres
centre = (pos.min(0) + pos.max(0)) / 2
pos -= centre                                  # centre bounding box on the origin
print('baked bounds (cm):', pos.min(0).round(2), pos.max(0).round(2), ' centre removed:', centre.round(2))
np.savez('heart_baked.npz', pos=pos, nrm=NRM, idx=I.reshape(-1, 3), centre=centre)

# ---- textures --------------------------------------------------------------------------
def jpeg(path, size, q, mode='RGB'):
    im = Image.open(path).convert(mode).resize((size, size), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); return b.getvalue()
diffuse = jpeg(f'{tex_dir}/gltf_embedded_0.png', 2048, 88)
normal = jpeg(f'{tex_dir}/gltf_embedded_2.png', 1024, 92)

# ---- GLB writer ------------------------------------------------------------------------
def pad4(b, p=b'\x00'): return b + p * ((4 - len(b) % 4) % 4)
chunks = []                                    # (bytes, target)
def add(b, target=None): chunks.append((pad4(b), target, len(b)))
add(pos.astype('<f4').tobytes(), 34962)
add(NRM.astype('<f4').tobytes(), 34962)
add(UV.astype('<f4').tobytes(), 34962)
assert P.shape[0] < 65536
add(I.astype('<u2').tobytes(), 34963)
add(diffuse); add(normal)
views, o = [], 0
for b, tgt, ln in chunks:
    v = {'buffer': 0, 'byteOffset': o, 'byteLength': ln}
    if tgt: v['target'] = tgt
    views.append(v); o += len(b)
binblob = b''.join(c[0] for c in chunks)

gltf = {
  'asset': {'version': '2.0', 'generator': 'tools/bake_heart.py',
            'copyright': 'Human_heart_3d_model by marxtrax (https://skfb.ly/oDKZq), CC BY 4.0. '
                         'Modified: rest pose baked to static mesh, re-centred, textures resized.'},
  'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'name': 'heart', 'mesh': 0}],
  'meshes': [{'name': 'heart', 'primitives': [{'attributes': {'POSITION': 0, 'NORMAL': 1, 'TEXCOORD_0': 2}, 'indices': 3, 'material': 0}]}],
  'materials': [{'name': 'heart_material', 'doubleSided': True,
                 'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}, 'metallicFactor': 0.0, 'roughnessFactor': 0.55},
                 'normalTexture': {'index': 1, 'scale': 1.0}}],
  'textures': [{'source': 0, 'sampler': 0}, {'source': 1, 'sampler': 0}],
  'samplers': [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497}],
  'images': [{'bufferView': 4, 'mimeType': 'image/jpeg'}, {'bufferView': 5, 'mimeType': 'image/jpeg'}],
  'accessors': [
    {'bufferView': 0, 'componentType': 5126, 'count': len(pos), 'type': 'VEC3',
     'min': pos.min(0).astype(float).tolist(), 'max': pos.max(0).astype(float).tolist()},
    {'bufferView': 1, 'componentType': 5126, 'count': len(NRM), 'type': 'VEC3'},
    {'bufferView': 2, 'componentType': 5126, 'count': len(UV), 'type': 'VEC2'},
    {'bufferView': 3, 'componentType': 5123, 'count': len(I), 'type': 'SCALAR'}],
  'bufferViews': views, 'buffers': [{'byteLength': len(binblob)}]}
js = pad4(json.dumps(gltf, separators=(',', ':')).encode(), b' ')
total = 12 + 8 + len(js) + 8 + len(binblob)
with open(out_path, 'wb') as fh:
    fh.write(struct.pack('<4sII', b'glTF', 2, total))
    fh.write(struct.pack('<I4s', len(js), b'JSON')); fh.write(js)
    fh.write(struct.pack('<I4s', len(binblob), b'BIN\x00')); fh.write(binblob)
print('wrote', out_path, total / 1e6, 'MB')
