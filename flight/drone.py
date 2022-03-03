from datetime import datetime, timezone
from mavsdk import System
from telemetry import TelemetryData
from communication import *
import asyncio
from movement import *
import requests

HOST = "http://localhost:3000"

def get_data(data, key, default=None):
    if key in data:
        return data[key]
    return default


def get_list_of_points(data, key):
    points = get_data(data, key, [])
    for i in range(len(points)):
        points[i] = data_to_mission_point(points[i])
    return points


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


class Mission:
    def __init__(self, data):
        self.id = data['id']
        
        self.lostCommsPos = data_to_mission_point(get_data(data, 'lostCommsPos', {}))
        
        self.flyZones = []
        if ('flyZones' in data):
            for zone in data['flyZones']:
                self.flyZones.append(FlyZone(zone))
        
        self.waypoints = get_list_of_points(data, 'waypoints')
        self.searchGridPoints = get_list_of_points(data, 'searchGridPoints')
        
        self.offAxisOdlcPos = data_to_mission_point(get_data(data, 'offAxisOdlcPos', {}))
        self.emergentLastKnowPos = data_to_mission_point(get_data(data, 'emergentLastKnowPos', {}))
        
        self.airDropBoundaryPoints = get_list_of_points(data, 'airDropBoundaryPoints')
        self.airDropsPos = data_to_mission_point(get_data(data, 'airDropPos', {}))
        self.ugvDrivePos = data_to_mission_point(get_data(data, 'ugvDrivePos', {}))

        self.stationaryObstacles = []
        if ('stationaryObstacles' in data):
            for obstacle in data['stationaryObstacles']:
                self.stationaryObstacles.append(data_to_obstacle(obstacle))

        self.mapCenterpos = data_to_mission_point(get_data(data, 'mapCenterPos', {}))
        self.mapHeight = get_data(data, 'mapHeight')


class Drone:
    def __init__(self):
        self.system = System()
        self.telemetry = TelemetryData()
        self.mission = None
        self.ground_altitude = 0
        self.last_contact = datetime.now(timezone.utc).timestamp()
        self.last_ground_contact = datetime.now(timezone.utc).timestamp()


    async def connect(self):
        await self.system.connect()
        print("Waiting for drone to connect...")
        async for state in self.system.core.connection_state():
            if state.is_connected:
                break
        print("Drone Connected Successfully!")


    def start_telemetry(self):
        asyncio.create_task(self.telemetry.position(self.system))
        asyncio.create_task(self.telemetry.landed(self.system))


    def start_heartbeat(self):
        if (test_connection()):
            # asyncio.create_task(telemetry_heartbeat(self.telemetry))
            # asyncio.create_task(self._get_mission())
            asyncio.create_task(self._heartbeat())

    async def _heartbeat(self):
        while True:
            result = requests.post(f"{HOST}/drone/heartbeat", json={
                "telemetryData": {
                    "latitude": self.telemetry.latitude,
                    "longitude": self.telemetry.longitude,
                    "altitude": self.telemetry.relative_altitude,
                    "heading": self.telemetry.yaw
                }
            })
            
            if (result.ok):
                data = result.json()
                self.last_contact = datetime.now(timezone.utc).timestamp()
                
                self.last_ground_contact = get_data(data, "lastGroundContact")
                # TODO: check if last_ground_contact is acceptable, otherwise return home 
                
                mission_id = get_data(data, "currentMissionId")
                if (mission_id is not None and (self.mission is None or self.mission.id != mission_id)):
                    await self._get_mission()
            
            await asyncio.sleep(1)


    async def _get_mission(self):
        result = requests.get(f"{HOST}/drone/mission")
        if (result.ok):
            mission_data = result.json()
            self.mission = Mission(mission_data)


    async def _finish_mission(self):
        pass

    
    async def takeoff(self):
        self.ground_altitude = self.telemetry.absolute_altitude
        await takeoff(self.system, self.telemetry)

    
    async def goto(self, latitude, longitude, altitude=None, yaw=0):
        if altitude is None:
            altitude = self.telemetry.absolute_altitude
        
        await goto_location(
            self.system, 
            self.telemetry, 
            latitude, 
            longitude, 
            altitude, 
            yaw)


    async def return_home(self):
        await return_to_home(self.system, self.telemetry)

    
    async def land(self):
        await land(self.system, self.telemetry)

