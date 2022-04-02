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
        points[i] = MissionPoint(points[i])
    return points

def create_mission_point(lat,long,alt):
    point=MissionPoint({})
    point.latitude=lat
    point.longitude=long
    point.altitude=alt
    return point

class MissionPoint:
    def __init__(self, data):
        self.next=None
        self.latitude = get_data(data, 'latitude')
        self.longitude = get_data(data, 'longitude')
        self.altitude = get_data(data, 'altitude')

class Obstacle(MissionPoint):
    def __init__(self, data):
        super().__init__(data)
        self.radius = get_data(data, 'radius')
        self.height = get_data(data, 'height')


class FlyZone:
    def __init__(self, data):
        self.altitudeMin = get_data(data, 'altitudeMin')
        self.altitudeMax = get_data(data, 'altitudeMax')
        self.boundaryPoints = get_list_of_points(data, 'boundaryPoints')


class Mission:
    def __init__(self, data):
        self.id = data['id']
        
        self.lostCommsPos = MissionPoint(get_data(data, 'lostCommsPos', {}))
        
        self.flyZones = []
        if ('flyZones' in data):
            for zone in data['flyZones']:
                self.flyZones.append(FlyZone(zone))
        
        self.waypoints = get_list_of_points(data, 'waypoints')
        self.searchGridPoints = get_list_of_points(data, 'searchGridPoints')
        
        self.offAxisOdlcPos = MissionPoint(get_data(data, 'offAxisOdlcPos', {}))
        self.emergentLastKnowPos = MissionPoint(get_data(data, 'emergentLastKnowPos', {}))
        
        self.airDropBoundaryPoints = get_list_of_points(data, 'airDropBoundaryPoints')
        self.airDropsPos = MissionPoint(get_data(data, 'airDropPos', {}))
        self.ugvDrivePos = MissionPoint(get_data(data, 'ugvDrivePos', {}))

        self.stationaryObstacles = []
        if ('stationaryObstacles' in data):
            for obstacle in data['stationaryObstacles']:
                self.stationaryObstacles.append(Obstacle(obstacle))

        self.mapCenterpos = MissionPoint(get_data(data, 'mapCenterPos', {}))
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
        #asyncio.create_task(self.telemetry.body(self.system)) # Issue: telemetry object does not have AngularVelocityBody()
        asyncio.create_task(self.telemetry.landed(self.system))
        #asyncio.create_task(self.telemetry.air(self.system))
        #asyncio.create_task(self.telemetry.ground_velocity(self.system)) # Issue: VelocityNed is a vector not a float
        asyncio.create_task(self.telemetry.angular_velocity(self.system))
        #asyncio.create_task(self.telemetry.acceleration(self.system)) # Issue: telemetry object does not have AccelerationFrd()
        asyncio.create_task(self.telemetry.battery_status(self.system))


    def start_heartbeat(self):
        if (test_connection()):
            # asyncio.create_task(telemetry_heartbeat(self.telemetry))
            # asyncio.create_task(self._get_mission())
            asyncio.create_task(self._heartbeat())

    async def _heartbeat(self):
        while True:
            
            # NOTE: Did not include is_in_air or is_landed because may not be
            #       necessary
            result = requests.post(f"{HOST}/drone/heartbeat", json={
                "telemetryData": {
                    "latitude": self.telemetry.latitude,
                    "longitude": self.telemetry.longitude,
                    "absolute_altitude": self.telemetry.absolute_altitude,
                    "relative_altitude": self.telemetry.relative_altitude,
                    "heading": self.telemetry.yaw,
                    #"is_in_air": self.telemetry.is_in_air,  # Enum?
                    #"is_landed": self.telemetry.is_landed,  # Enum
                    "roll": self.telemetry.roll,
                    "pitch": self.telemetry.pitch,
                    "yaw": self.telemetry.yaw,
                    "g_velocity": {
                        "north_m_s": self.telemetry.g_velocity.north_m_s,
                        "east_m_s": self.telemetry.g_velocity.east_m_s,
                        "down_m_s": self.telemetry.g_velocity.down_m_s,
                    },
                    "a_velocity": {
                        "roll_rad_s": self.telemetry.a_velocity.roll_rad_s,
                        "pitch_rad_s": self.telemetry.a_velocity.pitch_rad_s,
                        "yaw_rad_s": self.telemetry.a_velocity.yaw_rad_s
                    },
                    "forward": self.telemetry.forward,
                    "right": self.telemetry.right,
                    "down": self.telemetry.down,
                    #"battery": self.telemetry.battery # Issue: battery is not JSON serializable
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

    async def traverse_waypoints(self, points):
        for point in points:
            await self.goto(point.latitude, point.longitude, point.altitude, 0)

    async def airdrop(self):
        # TODO: Implement the airdrop method for drone.
        raise NotImplementedError

    async def return_home(self):
        await return_to_home(self.system, self.telemetry)

    
    async def land(self):
        await land(self.system, self.telemetry)

