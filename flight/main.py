import asyncio
from movement import *
from drone import *


async def main():
    drone = Drone()
    await drone.connect()

    print("Starting telemetry")
    drone.start_telemetry()

    print("Waiting for telemetry... ", end="")
    while not drone.telemetry.is_landed:
        await asyncio.sleep(1)
    print("Done!")

    print("Starting heartbeat.. ", end="")
    drone.start_heartbeat()
    print("Done!")
    
    await drone.takeoff()

    print(drone.ground_altitude)
    point1 = MissionPoint(38.1443,
                          -76.4250, drone.ground_altitude + 110)
    point2 = MissionPoint(38.1440,
                          -76.4260, drone.ground_altitude + 120)
    point3 = MissionPoint(38.1443,
                          -76.4260, drone.ground_altitude + 100)
    point4 = MissionPoint(38.1445,
                          -76.4300, drone.ground_altitude + 150)
    plist = [point1, point2, point3, point4]

    # TODO: Link-up drone telemetry to intermediary server so Garni can get the drone
    #       GPS and telemetry data for ground station map.

    await drone.traverse_waypoints(points=plist)

    await drone.return_home()
    await drone.land()

    await asyncio.sleep(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
