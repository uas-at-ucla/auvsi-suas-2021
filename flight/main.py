import asyncio
from movement import *
from waypoints import *
from drone import MissionPoint
from drone import create_mission_point
from drone import Drone

async def main():
    drone = Drone()
    await drone.connect()

    drone.start_telemetry()
    drone.start_heartbeat()

    while not drone.telemetry.is_landed:
        await asyncio.sleep(1)
    
    await drone.takeoff()

    plist=[
        MissionPoint(10, 10, drone.ground_altitude + 20), 
        MissionPoint(20, 20, drone.ground_altitude + 40),
        MissionPoint(40, 40, drone.ground_altitude + 80)
    ]

    await goto_waypoints(LinkedList(plist), drone)

    await drone.return_home()
    await drone.land()

    await asyncio.sleep(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
