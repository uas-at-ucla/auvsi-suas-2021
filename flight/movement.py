from typing import List
from mavsdk import System
from telemetry import TelemetryData
from utils import compare_altitude, compare_position, ft_to_m, draw_circle
import asyncio
from decouple import config
from drone import Obstacle

UPDATE_TIME = 1

OBSTACLE_BUFFER_SPACE = 4


# TODO: Add try/except for drone.action stuff
async def takeoff(
        drone: System,
        telemetry_data: TelemetryData,
        takeoff_alt: float = 100):
    """
    Takeoff procedure
        Parameters:
            drone - MAVSDK system
            telemetry_data - TelemetryData that holds the drone's most recent telemetry info
            takeoff_alt - altitude (in feet) to takeoff to
    """

    await drone.action.set_takeoff_altitude(ft_to_m(takeoff_alt))
    await drone.action.arm()
    await drone.action.takeoff()
    print("Taking Off")

    alt = telemetry_data.relative_altitude
    # Continue until takeoff altitude reached
    while alt is None or not compare_altitude(alt, takeoff_alt):
        await asyncio.sleep(UPDATE_TIME)
        alt = telemetry_data.relative_altitude
        print(f"ALTITUDE: {alt} ft")

    print("Takeoff Finished")


async def land(
    drone: System,
    telemetry_data: TelemetryData
):
    """
    Procedure to land
        Parameters:
            drone - MAVSDK system
            telemetry_data - TelemetryData that holds the drone's most recent telemetry info
    """

    await drone.action.land()
    print("Landing")

    alt = telemetry_data.relative_altitude
    while not compare_altitude(alt, 0, 1):
        print(f"ALTITUDE: {alt} ft")
        await asyncio.sleep(UPDATE_TIME)
        alt = telemetry_data.relative_altitude


async def goto_location(
        drone: System,
        telemetry_data: TelemetryData,
        lat: float,
        lon: float,
        alt: float,
        yaw: float):
    """
    Procedure to go to a location
        Parameters:
            drone - MAVSDK system
            telemetry_data - TelemetryData that holds the drone's most recent telemetry info
            lat - latitude (in degrees) to go to
            lon - longitude (in degrees) to go to
            alt - (absolutde) altitude (in feet) to go to
            yaw - yaw (in degrees) to position to
    """

    await drone.action.goto_location(lat, lon, ft_to_m(alt), yaw)
    print(f"Going to location ({lat}, {lon}, {alt})")

    # Wait until location reached
    while (not compare_position(
            (
                telemetry_data.latitude,
                telemetry_data.longitude,
                telemetry_data.absolute_altitude
            ), (lat, lon, alt))):

        print(
            f"LAT: {telemetry_data.latitude}, LON: {telemetry_data.longitude}, REL_ALT: {telemetry_data.relative_altitude}")
        await asyncio.sleep(UPDATE_TIME)

    print("Target location reached")


async def return_to_home(drone: System, data: TelemetryData):
    """
    Procedure to return home
        Parameters:
            drone - MAVSDK system
            telemetry_data - TelemetryData that holds the drone's most recent telemetry info
    """
    print("Returning Home")
    await goto_location(drone, data, HOME_LAT, HOME_LON, data.absolute_altitude, 0)


class DronePathfinder:
    def __init__(self, mission):
        self.set_mission(mission)
    
    def set_mission(self, mission):
        if mission.stationaryObstacles is not None:
            self.obstacles = mission.stationaryObstacles
            self.ox = []
            self.oy = []
            self._create_obstacles_points()
    
    def _create_obstacles_points(self):
        ox: List[int] = [] # Obstacle points x
        oy: List[int] = [] # Obstacle points y 
        
        obstacle: Obstacle
        for obstacle in self.obstacles:
            # TODO: figure out lon/lat conversion to int grid
            cx = obstacle.longitude
            cy = obstacle.latitude
            r = obstacle.radius + OBSTACLE_BUFFER_SPACE
            x_list, y_list = draw_circle(cx, cy, r)
            ox.extend(x_list)
            oy.extend(y_list)
            
        self.ox = ox
        self.oy = oy