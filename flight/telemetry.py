"""
Module for telemetry update coroutines.
"""
from mavsdk import System


class TelemetryData:
    """
    Stores telemetry data.
    """
    latitude = None
    longitude = None
    absolute_altitude = None
    relative_altitude = None


async def position(drone: System, telemetry_data: TelemetryData):
    """
    Coroutine to constantly update telemetry_data with latest position data
    """
    async for pos in drone.telemetry.position():
        telemetry_data.latitude = pos.latitude_deg
        telemetry_data.longitude = pos.longitude_deg
        telemetry_data.absolute_altitude = pos.absolute_altitude_m
        telemetry_data.relative_altitude = pos.relative_altitude_m
