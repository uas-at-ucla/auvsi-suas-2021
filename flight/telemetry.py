"""
Module for telemetry update coroutines.
"""
from mavsdk import System


def mps_to_kn(num):
    return num * 1.944


def m_to_ft(num):
    return num * 3.281


class TelemetryData:
    """
    Stores telemetry data.
    """
    latitude = None
    longitude = None
    absolute_altitude = None
    relative_altitude = None
    is_in_air = None
    is_landed = None
    roll = None
    pitch = None
    yaw = None
    g_velocity = None
    a_velocity = None
    forward = None
    right = None
    down = None
    battery = None


    async def position(self, drone: System):
        """
        Continue to constantly update telemetry_data with latest position data
        """
        async for pos in drone.telemetry.position():
            self.latitude = pos.latitude_deg
            self.longitude = pos.longitude_deg
            self.absolute_altitude = pos.absolute_altitude_m
            self.relative_altitude = pos.relative_altitude_m

            self.absolute_altitude = m_to_ft(self.absolute_altitude)
            self.relative_altitude = m_to_ft(self.relative_altitude)


    async def body(self, drone: System):
        async for turn in drone.telemetry.AngularVelocityBody():
            self.roll = turn.roll_rad_s
            self.pitch = turn.pitch_rad_s
            self.yaw = turn.yaw_rad_s


    async def landed(self, drone: System):
        async for is_landed in drone.telemetry.landed_state():
            self.is_landed = is_landed


    async def air(self, drone: System):
        async for is_in_air in drone.telemetry.in_air():
            self.is_in_air = is_in_air


    async def ground_velocity(self, drone: System):
        async for g_velocity in drone.telemetry.velocity_ned():
            self.g_velocity = mps_to_kn(g_velocity)


    async def angular_velocity(self, drone: System):
        async for a_velocity in drone.telemetry.attitude_angular_velocity_body():
            self.a_velocity = a_velocity


    async def acceleration(self, drone: System):
        async for acc in drone.telemetry.AccelerationFrd():
            self.forward = acc.forward_m_s2
            self.right = acc.right_m_s2
            self.down = acc.down_m_s2


    async def battery_status(self, drone: System):
        async for battery in drone.telemetry.battery():
            self.battery = battery


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
