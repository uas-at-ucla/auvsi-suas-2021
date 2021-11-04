from mavsdk import System
from telemetry import position, TelemetryData
import asyncio


HOME_LAT = 38.144478
HOME_LON = -76.42942
EPSILON = 0.01


def compare(x: float, y: float):
    if x is None or y is None: return False
    return abs(x - y) < EPSILON

async def takeoff(
    drone: System, 
    telemetry_data: TelemetryData, 
    takeoff_alt: float = 100):
    
    await drone.action.set_takeoff_altitude(takeoff_alt)
    await drone.action.arm()
    await drone.action.takeoff()
    print("Taking Off")

    alt = telemetry_data.relative_altitude
    # Continue until takeoff altitude reached
    while not compare(alt, takeoff_alt):
        await asyncio.sleep(1)
        alt = telemetry_data.relative_altitude

    print("Takeoff Finished")


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
    while (not compare(telemetry_data.latitude, lat) or
        not compare(telemetry_data.longitude, lon) or
        not compare(telemetry_data.absolute_altitude, alt)):
        
        await asyncio.sleep(1)
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
            print(f"Drone Connected Successfully!")
            break

    telemetry_data = TelemetryData()
    asyncio.create_task(position(drone, telemetry_data))
    
    await takeoff(drone, telemetry_data)
    # await goto_location(drone, telemetry_data, 38.144479, -76.42942, telemetry_data.absolute_altitude, 0)
    await return_to_home(drone, telemetry_data)

    asyncio.get_event_loop().stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())