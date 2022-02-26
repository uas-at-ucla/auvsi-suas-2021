import asyncio
from mavsdk import System
from telemetry import TelemetryData
from drone import MissionPoint

class LinkedList:
    def __init__(self):
        self.head=None

    def addToEnd(self,point):
        newmp=point
        if self.head is None:
            self.head=newmp
            return
        ptr=self.head
        while(ptr.next != None):
            ptr=ptr.next
        ptr.next=newmp

def createLinkedList(mplist,num):
    coords=LinkedList()
    coords.head=None
    for i in range(0,num,1): 
        coords.addToEnd(mplist[i])
    return coords

async def waypoints(orig_list, drone):

    i=len(orig_list)
    fin_list=createLinkedList(orig_list,i)
    current=fin_list.head

    while current is not None:
        await drone.goto(current.latitude, current.longitude, current.altitude,0)
        current=current.next


