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