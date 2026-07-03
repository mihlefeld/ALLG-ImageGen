import matplotlib.pyplot as plt
import numpy as np
from cubevis.colorizer import MegaminxColorizer

col = MegaminxColorizer()
verts = col.vertices
new_pts = np.zeros((6, 2))
new_pts[0] = verts[1] + (verts[1] - verts[16])
new_pts[1] = verts[1] + 2*(verts[1] - verts[16])
new_pts[2] = verts[0] + (verts[0] - verts[15])
new_pts[3] = verts[0] + 2*(verts[0] - verts[15])
new_pts[4] = verts[14] + (verts[14] - verts[29])
new_pts[5] = verts[14] + 2*(verts[14] - verts[29])
verts = np.concatenate([verts, new_pts])

plt.gca().invert_yaxis()
plt.scatter(verts[:, 0], verts[:, 1])
for i, (x, y)  in enumerate(verts):
    plt.text(x, y, f"{i}")
plt.tight_layout()
plt.axis('equal')
plt.savefig("test.png")