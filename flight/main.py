import asyncio
from movement import *

from mavsdk import System
from telemetry import TelemetryData, position, landed
from utils import compare_altitude, compare_position

HOME_LAT = 38.144478
HOME_LON = -76.42942
UPDATE_TIME = 1


async def main():
    drone = System()
    await drone.connect()

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone Connected Successfully!")
            break

    telemetry_data = TelemetryData()
    asyncio.create_task(position(drone, telemetry_data))
    asyncio.create_task(landed(drone, telemetry_data))

    await asyncio.sleep(1)

    await takeoff(drone, telemetry_data)
    await goto_location(
        drone,
        telemetry_data,
        38.144500,
        -76.42942,
        telemetry_data.absolute_altitude,
        0)

    await return_to_home(drone, telemetry_data)
    await land(drone, telemetry_data)

    await asyncio.sleep(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
