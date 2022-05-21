from ctypes import cast
from datetime import datetime, timezone
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from telemetry import TelemetryData
import communication as comms
import asyncio
from movement import *
from decouple import config
from utils import get_bearing

MAVLINK_PORT = config("MAVLINK", default=None)
USE_INTERMEDIARY = config("USE_INTERMEDIARY", default=False, cast=bool)
HOME_LAT = float(config("HOME_LAT", default="0"))
HOME_LON = float(config("HOME_LON", default="0"))
# from pixcam import PixCam
from utils import kn_to_ftps
from typing import Union

HEARTBEAT_RATE = 0.5
RTH_TIMEOUT = 30
LAND_TIMEOUT = 180

DRONE_SPEED = 1 # m/s because why not?
MISSION_POINT_TOL = 0.2

# ================================================================
#             Utils for JSON dictionary to objects
# ================================================================


def get_data(data, key, default=None):
    if key in data:
        return data[key]
    return default


def get_list_of_points(data, key):
    points = get_data(data, key, [])
    for i in range(len(points)):
        points[i] = data_to_mission_point(points[i])
    return points


# ================================================================
#      JSON dictionary to mission objects helper functions
# ================================================================

def data_to_mission_point(data):
    latitude = get_data(data, 'latitude')
    longitude = get_data(data, 'longitude')
    altitude = get_data(data, 'altitude')
    return MissionPoint(latitude, longitude, altitude)


def data_to_obstacle(data):
    latitude = get_data(data, 'latitude')
    longitude = get_data(data, 'longitude')
    altitude = get_data(data, 'altitude')
    radius = get_data(data, 'radius')
    height = get_data(data, 'height')
    return Obstacle(latitude, longitude, altitude, radius, height)


def data_to_flyzone(data):
    altitudeMin = get_data(data, 'altitudeMin')
    altitudeMax = get_data(data, 'altitudeMax')
    boundaryPoints = get_list_of_points(data, 'boundaryPoints')
    return FlyZone(altitudeMin, altitudeMax, boundaryPoints)


# =================================================================
#                       Mission Objects
# =================================================================

class MissionPoint:
    def __init__(self, latitude, longitude, altitude):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude


class Obstacle(MissionPoint):
    def __init__(self, latitude, longitude, altitude, radius, height):
        super().__init__(latitude, longitude, altitude)
        self.radius = radius
        self.height = height


class FlyZone:
    def __init__(self, altitudeMin, altitudeMax, boundaryPoints):
        self.altitudeMin = altitudeMin
        self.altitudeMax = altitudeMax
        self.boundaryPoints = boundaryPoints


# TODO: Refactor to use data_to_mission
# TODO: Add default values
class Mission:
    def __init__(self, data):
        self.id = data['id']

        self.lostCommsPos = data_to_mission_point(
            get_data(data, 'lostCommsPos', {}))

        self.flyZones = []
        if ('flyZones' in data):
            for zone in data['flyZones']:
                self.flyZones.append(data_to_flyzone(zone))
            if (len(data['flyZones']) > 0):
                self.flyZone = self.flyZones[0]

        self.waypoints = get_list_of_points(data, 'waypoints')
        self.searchGridPoints = get_list_of_points(data, 'searchGridPoints')

        self.offAxisOdlcPos = data_to_mission_point(
            get_data(data, 'offAxisOdlcPos', {}))
        self.emergentLastKnowPos = data_to_mission_point(
            get_data(data, 'emergentLastKnowPos', {}))

        self.airDropBoundaryPoints = get_list_of_points(
            data, 'airDropBoundaryPoints')
        self.airDropsPos = data_to_mission_point(
            get_data(data, 'airDropPos', {}))
        self.ugvDrivePos = data_to_mission_point(
            get_data(data, 'ugvDrivePos', {}))

        self.stationaryObstacles = []
        if ('stationaryObstacles' in data):
            for obstacle in data['stationaryObstacles']:
                self.stationaryObstacles.append(data_to_obstacle(obstacle))

        self.mapCenterPos = data_to_mission_point(
            get_data(data, 'mapCenterPos', {}))
        self.mapHeight = get_data(data, 'mapHeight')


# =================================================================
#                       Drone Object
# =================================================================

class Drone:
    def __init__(self, pic_rate: float=5):
        self.system = System()
        self.telemetry = TelemetryData()
        self.mission = None
        self.ground_altitude = 0
        self.last_contact = datetime.now(timezone.utc).timestamp()
        self.last_ground_contact = datetime.now(timezone.utc).timestamp()
        
        self.home_lat = HOME_LAT
        self.home_lon = HOME_LON

        self.PIC_RATE = pic_rate

    async def connect(self):
        '''Connects the Drone to the MAVSDK interface'''
        print("Waiting for drone to connect...")
        if MAVLINK_PORT is not None:
            print(f"Using connection port: {MAVLINK_PORT}")
            await self.system.connect(system_address=MAVLINK_PORT)
        else:
            await self.system.connect()
        async for state in self.system.core.connection_state():
            if state.is_connected:
                break        
        print("Drone Connected Successfully!")

        if USE_INTERMEDIARY:
            print("Awaiting connection to intermediary server...")
            while not comms.test_connection():
                await asyncio.sleep(1)
            print("Connected to server!")


    def start_telemetry(self,
        use_position=True,
        use_body=True,
        use_landed=True,
        use_air=True,
        use_ground_velocity=True,
        use_angular_velocity=True,
        use_acceleration=True,
        use_battery_status=True):
        '''Starts all the tasks for collecting telemetry data'''

        if use_position:
            asyncio.create_task(self.telemetry.position(self.system))
        if use_body:
            asyncio.create_task(self.telemetry.body(self.system))
        if use_landed:
            asyncio.create_task(self.telemetry.landed(self.system))
        if use_air:
            asyncio.create_task(self.telemetry.air(self.system))
        if use_ground_velocity:
            asyncio.create_task(self.telemetry.g_velocity(self.system))
        if use_angular_velocity:
            asyncio.create_task(self.telemetry.a_velocity(self.system))
        if use_acceleration:
            asyncio.create_task(self.telemetry.acceleration(self.system))
        if use_battery_status:
            asyncio.create_task(self.telemetry.battery_status(self.system))

    def start_heartbeat(self):
        '''Starts the heartbeat with the intermediary server'''

        if (USE_INTERMEDIARY or comms.test_connection()):
            asyncio.create_task(self._heartbeat())

    async def _heartbeat(self):
        '''Uploads data to the intermediary server and parses the response'''

        while True:
            data = await comms.post_heartbeat(self)
            if data is not None:
                self.last_contact = datetime.now(timezone.utc).timestamp()

                self.last_ground_contact = get_data(data, "lastGroundContact")
                # TODO: check if last_ground_contact is acceptable, otherwise return home

                mission_id = get_data(data, "currentMissionId")
                # print("HEARTBEAT!", data)
                if (mission_id is None or self.mission is None or self.mission.id != mission_id):
                    await self._get_mission()
            await asyncio.sleep(HEARTBEAT_RATE)

    async def _get_mission(self):
        '''Grabs mission data from the intermediary server and parses the response'''

        data = await comms.get_mission()
        if data is not None:
            self.mission = Mission(data)
            if self.mission.mapCenterPos is not None:
                self.home_lat = self.mission.mapCenterPos.latitude
                self.home_lon = self.mission.mapCenterPos.longitude
                print("Set home coords to: ", self.home_lat, self.home_lon)
        

    def start_picture_taking(self, working_dir: str):
        ''' 
        Start taking pictures for map stitching
            Parameters:
                working_dir: str - path to the working directory of the camera
        '''
        self.camera = PixCam(working_dir)
        if (self.camera.check_camera_connection()):
            asyncio.create_task(self._picture_taking())

    async def _picture_taking(self):
        while self.camera.check_camera_connection():
            t_data = self.telemetry
            
            img_path, _ = self.camera.take_pic_and_adjust_loc(
                lat=t_data.latitude,
                long=t_data.longitude,
                velocity=kn_to_ftps(t_data.ground_velocity.lateral_magnitude()),
                heading=t_data.yaw,
                alt=t_data.absolute_altitude
            )
            print("New picture saved at:", img_path)

            if not await comms.upload_image(img_path):
                print("Uploading picture to server FAILED")     
            await asyncio.sleep(self.PIC_RATE)

    async def takeoff(self, takeoff_alt: float=100):
        '''Starts the takeoff procedure, returns when takeoff is finished'''

        self.ground_altitude = self.telemetry.absolute_altitude
        await takeoff(self.system, self.telemetry, takeoff_alt)

    async def goto(self, latitude: float, longitude: float, relative_altitude: Union[float, None]=None, yaw=0):
        '''Goes to a specific location, return when arrived at location'''

        if relative_altitude is None:
            relative_altitude = self.telemetry.relative_altitude

        await goto_location(
            self.system,
            self.telemetry,
            latitude,
            longitude,
            relative_altitude + self.ground_altitude,
            yaw)

    async def traverse_waypoints(self, points: list):
        '''
        Travels through waypoints, returns when all points have been traversed
            Parameters:
                points: - list of MissionPoints
        '''
        current_lat = self.telemetry.latitude
        current_lon = self.telemetry.longitude
        current_alt = self.telemetry.relative_altitude
        
        mission_items = []
        for point in points:
            lat_list, lon_list = self.pathfinder.get_path(
                current_lat,
                current_lon,
                point.latitude,
                point.longitude
            )
            
            n = len(lat_list)
            d_alt = (point.altitude - current_alt) / n 
            
            next_lat = current_lat
            next_lon = current_lon
            for i in range(n):
                mission_items.append(
                    MissionItem(
                        lat_list[i],
                        lon_list[i],
                        current_alt + (d_alt * i),
                        DRONE_SPEED,
                        True,
                        0,
                        0,
                        MissionItem.CameraAction.NONE,
                        0,
                        0,
                        MISSION_POINT_TOL,
                        get_bearing(next_lat, next_lon, lat_list[i], lon_list[i])
                    )
                )
                next_lat = lat_list[i]
                next_lon = lon_list[i]
                
            current_lat = point.latitude
            current_lon = point.longitude
            current_alt = point.altitude
        mission_plan = MissionPlan(mission_items)
        await self.system.mission.upload_mission(mission_plan)
        await self.system.mission.start_mission()
        
        while (not await self.system.mission.is_mission_finished()):
            progress = await self.system.mission.mission_progress().__anext__
            print(f"Item: {progress.current}/{progress.total}, LAT: {self.telemetry.latitude}, LON: {self.telemetry.longitude}, REL_ALT: {self.telemetry.relative_altitude}")
            await asyncio.sleep(1)
        print("Mission Done")
        
            

    async def airdrop(self):
        # TODO: Implement the airdrop method for drone.
        raise NotImplementedError

    async def return_home(self):
        '''Start procedure to return home, returns when arrived'''

        # await return_to_home(self.system, self.telemetry)
        await self.goto(self.home_lat, self.home_lon, self.telemetry.relative_altitude)

    async def land(self):
        '''Start procedure to land, returns when landed'''

        await land(self.system, self.telemetry)

    async def start_mission(self):
        '''Starts running through the current mission
            - Requires that telemetry has been started and a mission be ready
        '''
        if (self.mission is None): return

        flyzones = self.mission.flyZones
        waypoints = self.mission.waypoints
        
        takeoff_alt = 100
        if (len(flyzones) > 0): 
            takeoff_alt = flyzones[0].altitudeMin + 10
            
        self.pathfinder = DronePathfinder(
            self.mission, 
            self.telemetry.latitude,
            self.telemetry.longitude
        )

        await self.takeoff(takeoff_alt)
        await self.traverse_waypoints(points=waypoints)
        await self.return_home()
        await self.land()

