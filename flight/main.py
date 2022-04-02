import asyncio
from venv import create
from movement import *
from waypoints import waypoints
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

    print(drone.ground_altitude)
    point1 = create_mission_point(38.14165971518743, -76.42502117913004, drone.telemetry.absolute_altitude)
    point2 = create_mission_point(38.14798800146675, -76.41875553886354, drone.telemetry.absolute_altitude)
    point3 = create_mission_point(38.15240903840184, -76.43581438821921, drone.telemetry.absolute_altitude)
    point4 = create_mission_point(38.142351634547964, -76.43441963952976, drone.telemetry.absolute_altitude)
    plist=[point1, point2, point3, point4]
    
    # TODO: Link-up drone telemetry to intermediary server so Garni can get the drone
    #       GPS and telemetry data for ground station map.

    # NEW
    # Moved the waypoints function into Drone class
    # ISSUE: Apparently, the drone will decrease altitude drastically when
    #        the altitude is set to "drone.ground_altitude".
    #        
    #        Printing "drone.ground_altitude" after takeoff resulted in this
    #        number: 1601.3413731384278
    #        The drone takeoff altitude is 100 feet at the time of testing. This
    #        is definitetly not 100 feet, and the meter to feet conversion is not
    #        100 feet either.
    #
    #        Doesn't seem to be an issue with MissionPoint, as it just wraps the
    #        coordinate data into a class object.
    #
    #        Possible areas to investigate would include:
    #           1. telemetry.py
    #           2. movement.py -> goto_location
    #           3. drone.py -> Drone -> goto
    #
    #        POSSIBLE SOLUTION: Seems to work when we use the drone's absolute altitude.
    #        
    #        ISSUE: I noticed that there seems to be a mixing of units in the code.
    #               Will need to check competition rules to see what units to work with,
    #               adjust accordingly, and document the code.
    await drone.traverse_waypoints(points=plist)

    await drone.return_home()
    await drone.land()

    await asyncio.sleep(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
