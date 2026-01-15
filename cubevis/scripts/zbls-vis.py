import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

import numpy as np

center = np.array([0, 0])
rot_matrix = Rotation.from_rotvec([0, 0, np.deg2rad(360/6)]).as_matrix()[:2, :2]
ubl = np.array([0, -1.0])
ubr = ubl @ rot_matrix
dbr = ubr @ rot_matrix
dfr = dbr @ rot_matrix
dfl = dfr @ rot_matrix
ufl = dfl @ rot_matrix



def interp(x, a, b):
    return a + x * (b-a)

def make_grid(a, b, c, d):
    edge_points = []
    for p1, p2 in [
        (a, b), 
        (d, c),
        (c, b), 
        (a, d),
    ]:
        edge_points.append(interp(1/3, p1, p2))
        edge_points.append(interp(2/3, p1, p2))
    c1 = interp(1/3, edge_points[0], edge_points[2])
    c2 = interp(2/3, edge_points[0], edge_points[2])
    c3 = interp(1/3, edge_points[1], edge_points[3])
    c4 = interp(2/3, edge_points[1], edge_points[3])
    all_points = [*edge_points[:-2], c1, c2, c3, c4, *edge_points[-2:]]
    return all_points

points = np.stack([center, ubl, ubr, dbr, dfr, dfl, ufl, *make_grid(center, ufl, ubl, ubr)[2:-2], *make_grid(center, dfr, dfl, ufl)[2:], *make_grid(ubr, dbr, dfr, center)])
plt.scatter(points[:, 0], points[:, 1])
for i, p in enumerate(points):
    plt.text(p[0] + 0.03, p[1], str(i))
print("        points = [")
for x, y in points:
    print(f"            [{x*100:.2f}, {y*100:.2f}],")
print("        ]")

# plt.axis("equal")
# plt.show()