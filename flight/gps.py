import asyncio
from mavsdk import System
#generates a mission with an array of tuples as lat and long coordinates.
#drone visits each of the coordinates in order of the array
async def generateMission(drone: System, coordinates):
    