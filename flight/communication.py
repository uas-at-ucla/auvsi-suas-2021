"""
Module for communicating with the Ground Station
"""
import asyncio
from datetime import datetime
from typing import Callable
from telemetry import TelemetryData
from mavsdk import System
import requests

HEARTBEAT_RATE = 0.5
RTH_TIMEOUT = 30
LAND_TIMEOUT = 180

HOST = "http://localhost:3000"

heartbeat_established = False
last_heartbeat = datetime.now()

def test_connection():
    try:
        result = requests.get(f"{HOST}/ping")
        return result.ok
    except:
        return False

async def telemetry_heartbeat(data: TelemetryData):
    # NOTE: Currently, to access telemetry data you will need to use the
    #       /ground/heartbeat endpoint.

    # NOTE: Did not include is_in_air or is_landed because may not be
    #       necessary
    
    while True:
        result = requests.post(f"{HOST}/drone/telemetry", json={
            "latitude": data.latitude,
            "longitude": data.longitude,
            "absolute_altitude": data.absolute_altitude,
            "relative_altitude": data.relative_altitude,
            "heading": data.yaw,
            "is_in_air": data.is_in_air,
            "is_landed": data.is_landed,
            "roll": data.roll,
            "pitch": data.pitch,
            "yaw": data.yaw,
            "g_velocity": data.g_velocity,
            "a_velocity": data.a_velocity,
            "forward": data.forward,
            "right": data.right,
            "down": data.down,
            "battery": data.battery
        })
        print(result.status_code, result.text)
        await asyncio.sleep(1)
