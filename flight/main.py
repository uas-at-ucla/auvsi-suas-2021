import asyncio
from movement import *
from drone import *
from mavsdk.telemetry import LandedState

async def main():
    drone = Drone()
    print("Connecting to drone...")
    await drone.connect()

    print("Starting telemetry")
    drone.start_telemetry()

    print("Waiting for telemetry... ", end="")
    while drone.telemetry.is_landed is None:
        await asyncio.sleep(1)
    print("Done!")
    
    print(f"Current telemetry: {drone.telemetry.__dict__}")

    print("Starting heartbeat... ", end="")
    drone.start_heartbeat()
    print("Done!")
    
    while drone.telemetry.latitude is None or \
        drone.telemetry.longitude is None:
        print(f"Awaiting GPS information... ")
        await asyncio.sleep(1)
    print("GPS confirmed!")

    if drone.telemetry.is_in_air:
        print("Landing first")
        await drone.return_home()
        await drone.land()
    
    print("Starting Mission")
    await asyncio.sleep(1)
    await drone.start_mission()

    await asyncio.sleep(1)
    print("FINISHED!")
    asyncio.get_event_loop().stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
