import asyncio

from mavsdk import System
from telemetry import TelemetryData
from utils import compare_altitude, compare_position

HOME_LAT = 38.144478
HOME_LON = -76.42942
UPDATE_TIME = 1

async def takeoff(
    drone: System,
    telemetry_data: TelemetryData,
    takeoff_alt: float = 30):

    await drone.action.set_takeoff_altitude(takeoff_alt)
    await drone.action.arm()
    await drone.action.takeoff()
    print("Taking Off")

    alt = telemetry_data.relative_altitude
    # Continue until takeoff altitude reached
    while not compare_altitude(alt, takeoff_alt):
        await asyncio.sleep(UPDATE_TIME)
        alt = telemetry_data.relative_altitude
        print(f"ALTITUDE: {alt}")

    print("Takeoff Finished")


async def land(
        drone: System,
        telemetry_data: TelemetryData
    ):

    await drone.action.land()
    print("Landing")

    alt = telemetry_data.relative_altitude
    while not compare_altitude(alt, 0, 1):
        print(f"ALTITUDE: {alt}")
        await asyncio.sleep(UPDATE_TIME)
        alt = telemetry_data.relative_altitude


async def goto_location(
    drone: System,
    telemetry_data: TelemetryData,
    lat: float,
    lon: float,
    alt: float,
    yaw: float):

    await drone.action.goto_location(lat, lon, alt, yaw)
    print(f"Going to location ({lat}, {lon}, {alt})")

    # Wait until location reached
    while (not compare_position(
        (
            telemetry_data.latitude,
            telemetry_data.longitude,
            telemetry_data.absolute_altitude
        ), (lat, lon, alt))):

        print(f"LAT: {telemetry_data.latitude}, LON: {telemetry_data.longitude}")
        await asyncio.sleep(UPDATE_TIME)

    print("Target location reached")


async def return_to_home(drone: System, data: TelemetryData):
    print("Returning Home")
    await goto_location(drone, data, HOME_LAT, HOME_LON, data.absolute_altitude, 0)


async def main():
    drone = System()
    await drone.connect()

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone Connected Successfully!")
            break

    t_data = TelemetryData()
    asyncio.create_task(t_data.position(drone))
    asyncio.create_task(t_data.landed(drone))

    while not t_data.is_landed:
        await asyncio.sleep(1)

    await takeoff(drone, t_data)
    await goto_location(
        drone,
        t_data,
        38.144500,
        -76.42942,
        t_data.absolute_altitude,
        0)

    await return_to_home(drone, t_data)
    await land(drone, t_data)

    await asyncio.sleep(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
