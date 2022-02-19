import asyncio
from mavsdk import System
from telemetry import TelemetryData

class Node:
    def __init__(self, lat=None, long=None,flying_alt=None, yaw=None):
        self.lat=lat
        self.long=long
        self.flying_alt=flying_alt
        self.yaw=yaw
        self.next=None
class LinkedList:
    def __init__(self):
        self.head=None

async def toLinkedList(lst,num):
    coords=LinkedList()
    coords=None
    for i in range(0,num,1):
        temp=lst(i)
        if(coords==None):
            coords=temp
        else:
            ptr=coords
            while(coords.next!=None):
                ptr=ptr.next
            ptr.next=temp
    return coords
    
async def waypoints(orig_list):
    
    drone = System()
    await drone.connect(system_address="udp://:14540")
    
    i=len(orig_list)
    fin_list=toLinkedList(orig_list,i)
    current=fin_list.head
    
    while current is not None:
        drone.action.goto_location(current.lat, current.long, current.flying_alt, current.yaw)
        current=current.next
    
