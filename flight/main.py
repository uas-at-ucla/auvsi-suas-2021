from mavsdk import System
import asyncio


async def main():
    drone = System()
    await drone.connect()

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone Connected Successfully!")
            break


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())