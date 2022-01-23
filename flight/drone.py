from mavsdk import System
from telemetry import TelemetryData
from communication import *
import asyncio
from movement import *

class Drone:
    def __init__(self):
        self.system = System()
        self.telemetry = TelemetryData()


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
            asyncio.create_task(telemetry_heartbeat(self.telemetry))

    
    async def takeoff(self):
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
