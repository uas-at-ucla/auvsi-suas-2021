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
    while True:
        result = requests.post(f"{HOST}/drone/telemetry", json={
            "latitude": data.latitude,
            "longitude": data.longitude,
            "altitude": data.relative_altitude,
            "heading": data.yaw
        })
        print(result.status_code, result.text)
        await asyncio.sleep(1)
