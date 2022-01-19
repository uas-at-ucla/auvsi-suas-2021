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

async def heartbeat(data: TelemetryData, mission_data):
    """
    Establishes heartbeat with the ground station server
    1. Upload Telemetry data
    2. Get mission
    """
    while True:
        # result = requests.POST(server, body=data.to_json())
        # if result.status == 200:
        #   heartbeat_established = true
        #   last_heartbeat = datetime.now()
        #   mission_data.update(result.json())
        # else:
        #   heartbeat_established = false
        #   timeout = datetime.now() - last_heartbeat
        #   if timeout >= RTH_TIMEOUT: return_to_home()
        #   else if timeout >= LAND_TIMEOUT: land()
        await asyncio.sleep(HEARTBEAT_RATE)
