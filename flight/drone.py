from datetime import datetime, timezone
from mavsdk import System
from telemetry import TelemetryData
import communication as comms
import asyncio
from movement import *
from decouple import config


HEARTBEAT_RATE = 0.5
RTH_TIMEOUT = 30
LAND_TIMEOUT = 180

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

        self.mapCenterpos = data_to_mission_point(
            get_data(data, 'mapCenterPos', {}))
        self.mapHeight = get_data(data, 'mapHeight')


# =================================================================
#                       Drone Object
# =================================================================

class Drone:
    def __init__(self):
        self.system = System()
        self.telemetry = TelemetryData()
        self.mission = None
        self.ground_altitude = 0
        self.last_contact = datetime.now(timezone.utc).timestamp()
        self.last_ground_contact = datetime.now(timezone.utc).timestamp()

    async def connect(self):
        '''Connects the Drone to the MAVSDK interface'''
        port = config("MAVlink", default=None)
        if port is not None:
            print(f"Using connection port: {port}")
            await self.system.connect(system_address=port)
        else:
            await self.system.connect()
        print("Waiting for drone to connect...")
        async for state in self.system.core.connection_state():
            if state.is_connected:
                break
        print("Drone Connected Successfully!")

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
            asyncio.create_task(self.telemetry.ground_velocity(self.system))
        if use_angular_velocity:
            asyncio.create_task(self.telemetry.angular_velocity(self.system))
        if use_acceleration:
            asyncio.create_task(self.telemetry.acceleration(self.system))
        if use_battery_status:
            asyncio.create_task(self.telemetry.battery_status(self.system))

    def start_heartbeat(self):
        '''Starts the heartbeat with the intermediary server'''

        if (comms.test_connection()):
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
                if (mission_id is not None and (self.mission is None or self.mission.id != mission_id)):
                    await self._get_mission()
            await asyncio.sleep(HEARTBEAT_RATE)

    async def _get_mission(self):
        '''Grabs mission data from the intermediary server and parses the response'''

        data = await comms.get_mission(self)
        if data is not None:
            self.mission = Mission(data)

    async def takeoff(self, takeoff_alt=100):
        '''Starts the takeoff procedure, returns when takeoff is finished'''

        self.ground_altitude = self.telemetry.absolute_altitude
        await takeoff(self.system, self.telemetry, takeoff_alt)

    async def goto(self, latitude, longitude, relative_altitude=None, yaw=0):
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

    async def traverse_waypoints(self, points):
        '''
        Travels through waypoints, returns when all points have been traversed
            Parameters:
                points - list of MissionPoints
        '''

        for point in points:
            # TODO: Add pathfinding + smoothing algorithm
            await self.goto(point.latitude, point.longitude, point.altitude, 0)

    async def airdrop(self):
        # TODO: Implement the airdrop method for drone.
        raise NotImplementedError

    async def return_home(self):
        '''Start procedure to return home, returns when arrived'''

        await return_to_home(self.system, self.telemetry)

    async def land(self):
        '''Start procedure to land, returns when landed'''

        await land(self.system, self.telemetry)

    async def start_mission(self):
        '''Starts running through the current mission
            - Requires that telemetry has been started
        '''
        if (self.mission is None): return

        flyzones = self.mission.flyZones
        waypoints = self.mission.waypoints
        
        takeoff_alt = 100
        if (len(flyzones) > 0): 
            takeoff_alt = flyzones[0].altitudeMin + 10

        await self.takeoff(takeoff_alt)
        await self.traverse_waypoints(points=waypoints)
        await self.return_home()
        await self.land()

