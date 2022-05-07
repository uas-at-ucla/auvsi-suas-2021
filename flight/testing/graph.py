# Testing for AStar and obstacle creation algorithms
import sys
sys.path.append('../')

import matplotlib.pyplot as plt
from utils import *
from astar import AStar
from datetime import datetime

# Initialize testing values
drone_radius = 1
sx, sy = -20.43, -20.1234
ex, ey = 20.5321, 20.1234
obstacle_buffer = 5
cx, cy = 0, 0
obstacle_radius = 10

# Calculate obstacle circle
ox, oy = draw_circle(cx, cy, obstacle_radius + obstacle_buffer)
bx, by = draw_border(-30, -30, 30, 30)
ox.extend(bx)
oy.extend(by)

# Draw obstace, start, and end
plt.plot(ox, oy, ".k", alpha=0.5)
plt.plot(sx, sy, 'og')
plt.plot(ex, ey, 'xb')
plt.grid(True)
plt.axis('equal')

# Calculate path
start = datetime.now()
pathfinder = AStar(ox, oy, 1, drone_radius)
rx, ry = pathfinder.planning(sx, sy, ex, ey)
end = datetime.now()
print(f"TIME ELAPSED: {end-start}")

# Draw path
plt.plot(rx, ry, '-r')
plt.show()