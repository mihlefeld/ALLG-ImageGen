from scipy.spatial.transform import Rotation
import numpy as np

r2 = np.sqrt(2)
side_len = 2*r2 + 1
r3 = r2 + 1
r5 = side_len
e2 = 0.35 * 2
e1 = e2 - 0.03
c2 = 0.43 * 2
c1 = c2 - 0.03
ext = -0.4
def make_eary_exit_points(a, b, c, r1, r2):
    a = np.array(a)
    b = np.array(b)
    mp_ab = a + (b - a) / 2
    mp_ac = a + (c - a) * r1
    mp_bc = b + (c - b) * r1
    mp_abc = mp_ab + (c - mp_ab) * r2
    return (tuple(mp_ac), tuple(mp_abc), tuple(mp_bc))

center = (r5/2, r5/2)

def extend_point(x, c, r):
    x = np.array(x)
    return tuple(x + (c - x) * r)
    

points = [
    (0, 0), 
    (0, r2),
    (0, r3),
    (0, r5),
    (r2, r5),
    (r3, r5),
    (r5, r5),
    (r5, r3),
    (r5, r2),
    (r5, 0),
    (r3, 0),
    (r2, 0),
]
points += [
    *make_eary_exit_points(points[11], points[1], center, c1, c2),
    *make_eary_exit_points(points[1], points[2], center, e1, e2),
    *make_eary_exit_points(points[2], points[4], center, c1, c2),
    *make_eary_exit_points(points[4], points[5], center, e1, e2),
    *make_eary_exit_points(points[5], points[7], center, c1, c2),
    *make_eary_exit_points(points[7], points[8], center, e1, e2),
    *make_eary_exit_points(points[8], points[10], center, c1, c2),
    *make_eary_exit_points(points[10], points[11], center, e1, e2),
    *[extend_point(points[i], center, ext) for i in range(12)]
]
points = np.array(points)
# points_down = np.array(points)
# points_down[:, 1] -= r5 * 1.8
# points = np.concatenate([points, points_down], axis=0)
original = len(points)

import matplotlib.pyplot as plt
plt.axis("equal")
plt.scatter(points[:original, 0], points[:original, 1])

for i, (x, y) in enumerate(points[:original]):
    plt.text(x, y, f"{i}")
plt.show()

points[:, 1] = r5 - points[:, 1]
points *= 50
print("        points = [")
for x, y in points:
    print(f"            ({x:.2f}, {y:.2f}),")
print("        ]")