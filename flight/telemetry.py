from mavsdk import System
from mavsdk.telemetry_pb2 import Position


class TelemetryData:
    latitude = None
    longitude = None
    absolute_altitude = None
    relative_altitude = None


async def position(drone: System, telemetry_data: TelemetryData):
    async for position in drone.telemetry.position():
        telemetry_data.latitude = position.latitude_deg
        telemetry_data.longitude = position.longitude_deg
        telemetry_data.absolute_altitude = position.absolute_altitude_m
        telemetry_data.relative_altitude = position.relative_altitude_m

