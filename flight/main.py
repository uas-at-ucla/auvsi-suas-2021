import asyncio
from movement import *

from mavsdk import System
from telemetry import TelemetryData
from ground_station import telemetry_heartbeat

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

    asyncio.create_task(telemetry_heartbeat(t_data))

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
