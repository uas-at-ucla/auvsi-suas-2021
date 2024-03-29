from mavsdk import System
from astar import AStar
from telemetry import TelemetryData
from utils import *
import asyncio
from decouple import config

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


class DronePathfinder:
    def __init__(self, mission, start_lat, start_lon, width = 1000, height = 1000):
        self.width = width
        self.height = height
        
        self.min_latitude = None
        self.max_latitude = None
        self.delta_latitude = None
        self.min_longitude = None
        self.max_longitude = None
        self.delta_longitude = None
        
        self.a_star = None
        
        self.set_mission(mission, start_lat, start_lon)
    
    def set_mission(self, mission, start_lat, start_lon):
        if (mission.stationaryObstacles is None): 
            return
        if (mission.flyZone is None):
            return
        if (mission.flyZone.boundaryPoints is None): 
            return
        if (mission.waypoints is None):
            return
        
        self.obstacles = mission.stationaryObstacles
        self.boundaryPoints = mission.flyZone.boundaryPoints
        self.ox = []
        self.oy = []
        self.x_route = []
        self.y_route = []
        self.wp_x = []
        self.wp_y = []
        
        self._create_world_map()
        
        current_x, current_y = self._convert_coords(start_lat, start_lon)
        self.sx, self.sy = current_x, current_y
        
        self.a_star = AStar(self.ox, self.oy, 1, OBSTACLE_BUFFER_SPACE)
        self.waypoints = mission.waypoints
        for i, waypoint in enumerate(self.waypoints):
            x, y = self._convert_coords(waypoint.latitude, waypoint.longitude)
            self.wp_x.append(x)
            self.wp_y.append(y)

    def run_mission(self):
        start = self.waypoints[0]
        start_lat, start_lon = start.latitude, start.longitude
        self._traverse_waypoints(start_lat, start_lon, self.waypoints)
        
    def get_path(self, s_lat, s_lon, g_lat, g_lon):
        sx, sy = self._convert_coords(s_lat, s_lon)
        gx, gy = self._convert_coords(g_lat, g_lon)
        print(f"Pathing from {s_lat}, {s_lon} to {g_lat}, {g_lon}...", end="")
        x_list, y_list = self.a_star.planning(gx, gy, sx, sy)
        x_list, y_list = self._clean_route(x_list, y_list)
        print("DONE")
        
        # Convert x_list, y_list to latitude and longitude
        lat_list, lon_list = [], []
        n = len(x_list)
        for i in range(n):
            lat, lon = self._deconvert_coords(x_list[i], y_list[i])
            lat_list.append(lat)
            lon_list.append(lon)
        return lat_list, lon_list

    def _convert_coords(self, lat, lon):
        new_x, new_y = scale_coords(lon - self.min_longitude, lat - self.min_latitude, self.delta_longitude, self.delta_latitude, self.width, self.height) 
        return round(new_x), round(new_y)
    
    def _deconvert_coords(self, x, y):
        lon, lat = scale_coords(x, y, self.width, self.height, self.delta_longitude, self.delta_latitude)
        return lat + self.min_latitude, lon + self.min_longitude

    def _traverse_waypoints(self, start_lat, start_lon, waypoints):
        current_x, current_y = self._convert_coords(start_lat, start_lon)
        self.sx, self.sy = current_x, current_y
        for i, waypoint in enumerate(waypoints):
            x, y = self._convert_coords(waypoint.latitude, waypoint.longitude)
            self.wp_x.append(x)
            self.wp_y.append(y)
            
            print(i, current_x, current_y, x, y)
            
            x_list, y_list = self.a_star.planning(x, y, current_x, current_y)
            x_list, y_list = self._clean_route(x_list, y_list)
            self.x_route.extend(x_list)
            self.y_route.extend(y_list)
            
            current_x, current_y = x, y
    
    def _clean_route(self, x_list, y_list):
        n = len(x_list)
        if n < 2:
            return x_list, y_list
        new_x_list = [x_list[0]]
        new_y_list = [y_list[0]]
        current = 1
        while current < n - 1:
            x0 = new_x_list[-1]
            y0 = new_y_list[-1]
            x1 = x_list[current + 1]
            y1 = y_list[current + 1]
            flag = True
            for p in zip(*draw_line(x0, y0, x1, y1, thickness=0, max_x=self.width, max_y=self.height)):
                if ((p[0], p[1]) in self.obstacle_points):
                    flag = False
                    break
            if not flag:
                new_x_list.append(x_list[current])
                new_y_list.append(y_list[current])
            current += 1
        new_x_list.append(x_list[-1])
        new_y_list.append(y_list[-1])
        return new_x_list, new_y_list
            

    def _create_world_map(self):
        self.min_latitude = self.boundaryPoints[0].latitude
        self.max_latitude = self.boundaryPoints[0].latitude
        self.min_longitude = self.boundaryPoints[0].longitude
        self.max_longitude = self.boundaryPoints[0].longitude
        
        for bp in self.boundaryPoints:
            lat = bp.latitude
            lon = bp.longitude
            self.min_latitude = min(self.min_latitude, lat)
            self.max_latitude = max(self.max_latitude, lat)
            self.min_longitude = min(self.min_longitude, lon)
            self.max_longitude = max(self.max_longitude, lon)
    
        self.delta_latitude = self.max_latitude - self.min_latitude
        self.delta_longitude = self.max_longitude - self.min_longitude
        
        print(f"Delta Latitude: {self.delta_latitude}")
        print(f"Delta Longitude: {self.delta_longitude}")
        
        self._create_borders()
        self._create_obstacles_points()
        
        self.obstacle_points = set()
        for p in zip(self.ox, self.oy):
            self.obstacle_points.add((p[0], p[1]))
    
    def _create_borders(self):
        n = len(self.boundaryPoints)
        for i in range(n):
            bp0 = self.boundaryPoints[i]
            lat0 = bp0.latitude
            lon0 = bp0.longitude
            x0, y0 = self._convert_coords(lat0, lon0)

            bp1 = self.boundaryPoints[(i+1) % n]
            lat1 = bp1.latitude
            lon1 = bp1.longitude
            x1, y1 = self._convert_coords(lat1, lon1)
            
            x_list, y_list = draw_line(x0, y0, x1, y1, max_x=self.width, max_y=self.height)
            self.ox.extend(x_list)
            self.oy.extend(y_list)
            
    
    def _create_obstacles_points(self):
        for obstacle in self.obstacles:
            c_lat = obstacle.latitude
            c_lon = obstacle.longitude
            radius = obstacle.radius + OBSTACLE_BUFFER_SPACE
            lat_r = int(radius / 364_000 / self.delta_latitude * self.height)
            lon_r = int(radius / 288_200 / self.delta_longitude * self.height)
            r = max(lat_r, lon_r)
            print(r)
            cx, cy = self._convert_coords(c_lat, c_lon)
            x_list, y_list = draw_octagon(cx, cy, r, max_x=self.width, max_y=self.height)
            self.ox.extend(x_list)
            self.oy.extend(y_list)