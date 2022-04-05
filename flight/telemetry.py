# TODO: Need documentation

"""
Module for telemetry update coroutines.
"""
from mavsdk import System
from utils import mps_to_kn, m_to_ft


class VelocityNedKnots:
    def __init__(self, north_kn, east_kn, down_kn):
        self.north_kn = north_kn
        self.east_kn = east_kn
        self.down_kn = down_kn


class TelemetryData:
    """
    Stores telemetry data.
    """
    # Property:                 # Units:
    latitude = None             # degrees
    longitude = None            # degrees
    absolute_altitude = None    # feet
    relative_altitude = None    # feet
    is_in_air = None            # bool
    is_landed = None            # mavsdk.telemetry.LandedState enum
    roll = None                 # degrees
    pitch = None                # degrees
    yaw = None                  # degrees
    ground_velocity = None      # knots
    angular_velocity = None     # rad/s
    forward = None              # TBD
    right = None                # TBD
    down = None                 # TBD
    battery_volts = None        # volts
    battery_remaining = None    # percent

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
        async for turn in drone.telemetry.attitude_euler():
            self.roll = turn.roll_deg
            self.pitch = turn.pitch_deg
            self.yaw = turn.yaw_deg

    async def landed(self, drone: System):
        async for is_landed in drone.telemetry.landed_state():
            self.is_landed = is_landed

    async def air(self, drone: System):
        async for is_in_air in drone.telemetry.in_air():
            self.is_in_air = is_in_air

    async def ground_velocity(self, drone: System):
        async for g_velocity in drone.telemetry.velocity_ned():
            self.ground_velocity = VelocityNedKnots(
                mps_to_kn(g_velocity.north_m_s),
                mps_to_kn(g_velocity.east_m_s),
                mps_to_kn(g_velocity.down_m_s),
            )

    async def angular_velocity(self, drone: System):
        async for a_velocity in drone.telemetry.attitude_angular_velocity_body():
            self.angular_velocity = a_velocity

    # TODO: convert to ft or kn per s2
    async def acceleration(self, drone: System):
        async for imu in drone.telemetry.imu():
            acc = imu.acceleration_frd
            self.forward = acc.forward_m_s2
            self.right = acc.right_m_s2
            self.down = acc.down_m_s2

    async def battery_status(self, drone: System):
        async for battery in drone.telemetry.battery():
            self.battery_volts = battery.voltage_v
            self.battery_remaining = battery.remaining_percent


# telemetry data needed
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
