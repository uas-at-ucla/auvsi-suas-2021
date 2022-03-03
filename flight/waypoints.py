import asyncio
from mavsdk import System
from telemetry import TelemetryData
from drone import MissionPoint


class LinkedListNode:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

    def attach(self, node):
        self.next = node
        node.prev = self

    def __next__(self):
        if self.next is None:
            raise StopIteration
        return self.next


class LinkedList:
    def __init__(self, data_list = None):
        self.head = None
        self.tail = None

        if data_list is not None:
            self._generate_from_list(data_list)

    def __iter__(self):
        return self.head

    def _generate_from_list(self, data_list):
        for data in data_list:
            self.addToEnd(data)

    def addToEnd(self, data):
        node = LinkedListNode(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            self.tail.attach(node)
            self.tail = node


async def goto_waypoints(waypoints, drone):    
    for current in waypoints:
        # TODO: replace with proper pathing
        await drone.goto(current.latitude, current.longitude, current.altitude, 0)
