# Testing for AStar and obstacle creation algorithms
import sys
sys.path.append('../')

from drone import Drone
import matplotlib.pyplot as plt
from utils import *
from astar import AStar
from datetime import datetime
from communication import get_mission
from drone import Mission
from movement import DronePathfinder
import asyncio
import math

# Initialize testing values
drone_radius = 1

mission = asyncio.get_event_loop().run_until_complete(get_mission())
mission = Mission(mission)
start_lat = mission.mapCenterPos.latitude
start_lon = mission.mapCenterPos.longitude

pathfinder = DronePathfinder(mission, start_lat, start_lon, 500, 500)

# Draw obstace, start, and end
plt.plot(pathfinder.ox, pathfinder.oy, ".k", alpha=0.5)
plt.plot(pathfinder.sx, pathfinder.sy, 'og')
plt.plot(pathfinder.wp_x, pathfinder.wp_y, 'xb')

plt.grid(True)
plt.axis('equal')

plt.show()

if (True):
    start = datetime.now()
    pathfinder.run_mission()
    end = datetime.now()
    print(f"TIME ELAPSED: {end-start}")

    # Draw path
    plt.plot(pathfinder.ox, pathfinder.oy, ".k", alpha=0.5)
    plt.plot(pathfinder.sx, pathfinder.sy, 'og')
    plt.plot(pathfinder.wp_x, pathfinder.wp_y, 'xb')

    plt.grid(True)
    plt.axis('equal')
    plt.plot(pathfinder.x_route, pathfinder.y_route, '-r')

    plt.show()