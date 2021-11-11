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
    is_landed = None


async def position(drone: System, telemetry_data: TelemetryData):
    """
    Coroutine to constantly update telemetry_data with latest position data
    """
    async for pos in drone.telemetry.Position():
        telemetry_data.latitude = pos.latitude_deg
        telemetry_data.longitude = pos.longitude_deg
        telemetry_data.absolute_altitude = pos.absolute_altitude_m
        telemetry_data.relative_altitude = pos.relative_altitude_m

async def body(drone:System, telemetry_data: TelemetryData):
    async for turn in drone.telemetry.AngularVelocityBody():
        telemetry_data.roll=turn.roll_rad_s
        telemetry_data.pitch=turn.pitch_rad_s
        telemetry_data.yaw=turn.yaw_rad_s
        
async def landed(drone: System, telemetry_data: TelemetryData):
    async for is_landed in drone.telemetry.landed_state():
        telemetry_data.is_landed = is_landed

async def air(drone: System, telemetry_data: TelemetryData):
    async for is_in_air in drone.telemetry.in_air():
        telemetry_data.is_in_air = is_in_air
        
async def ground_velocity(drone: System, telemetry_data: TelemetryData):
    async for g_velocity in drone.telemetry.velocity_ned():
        telemetry_data.g_velocity= g_velocity

async def angular_velocity(drone: System, telemetry_data: TelemetryData):
    async for a_velocity in drone.telemetry.attitude_angular_velocity_body():
        telemetry_data.a_veloc
        ity= a_velocity
        
async def acceleration(drone:System, telemetry_data: TelemetryData):
    async for acc in drone.telemetry.AccelerationFrd():
        telemetry_data.forward=acc.forward_m_s2
        telemetry_data.right=acc.right_m_s2
        telemetry_data.down=acc.down_m_s2

async def battery(drone:System, telemetry_data: TelemetryData):
    async for battery in drone.telemetry.battery():
        telemetry_data.battery=battery

#telemetry data needed
'''
gps coordinates  - check
angles           - check
altitude         - check
acceleration     - check
speed            - check
battery          - check   
flight status    
    ground       - check
    air          - check
'''


