"""
Module for communicating with the Intermediary Server
"""
import asyncio
from datetime import datetime
from typing import Callable
from telemetry import TelemetryData
from mavsdk import System
import requests
from utils import ft_to_m


HOST = "http://localhost:3000" # TODO: Use config file for HOST name

heartbeat_established = False
last_heartbeat = datetime.now()


def test_connection():
    try:
        result = requests.get(f"{HOST}/ping")
        return result.ok
    except:
        return False


async def post_heartbeat(drone):
    # NOTE: Did not include is_in_air or is_landed because may not be
    #       necessary
    result = requests.post(f"{HOST}/drone/heartbeat", json={
        "telemetryData": {
            "latitude": drone.telemetry.latitude,
            "longitude": drone.telemetry.longitude,
            "absolute_altitude": drone.telemetry.absolute_altitude,
            "relative_altitude": drone.telemetry.relative_altitude,
            "heading": drone.telemetry.yaw,
            # "is_in_air": drone.telemetry.is_in_air,  # Enum?
            # "is_landed": drone.telemetry.is_landed,  # Enum
            "roll": drone.telemetry.roll,
            "pitch": drone.telemetry.pitch,
            "yaw": drone.telemetry.yaw,
            "g_velocity": {
                "north_m_s": drone.telemetry.g_velocity.north_m_s,
                "east_m_s": drone.telemetry.g_velocity.east_m_s,
                "down_m_s": drone.telemetry.g_velocity.down_m_s,
            } if drone.telemetry.g_velocity is not None else None,
            "a_velocity": {
                "roll_rad_s": drone.telemetry.a_velocity.roll_rad_s,
                "pitch_rad_s": drone.telemetry.a_velocity.pitch_rad_s,
                "yaw_rad_s": drone.telemetry.a_velocity.yaw_rad_s
            } if drone.telemetry.a_velocity is not None else None,
            "forward": drone.telemetry.forward,
            "right": drone.telemetry.right,
            "down": drone.telemetry.down,
            # "battery": drone.telemetry.battery # Issue: battery is not JSON serializable
        }
    })

    if (result.ok):
        return result.json()
    else:
        return None


async def get_mission(drone):
    result = requests.get(f"{HOST}/drone/mission")
    if (result.ok):
        return result.json()
    else:
        return None
