import asyncio, time
from xmlrpc.client import SERVER_ERROR
from mavsdk import System
from mavsdk import telemetry
import requests
import numpy as np

END_STATE = 2
DETACH_THRESH = 1 # TODO

SERVER_ROUTE = 'localhost:3000/ugv'

def dist_to_ground():
    return 0.5 # TEMP
    pass # TODO

def detach_from_uas():
    pass # TODO 10sec wait

def report_mission_sucess():
    pass # TODO

def post(path, data):
    try:
        result = requests.post(path, json=data)

        if (result.ok):
            return result.json()
        else:
            return None
    except Exception as e:
        print(e)
        return None
def get(path):
    try:
        result = requests.get(path)

        if (result.ok):
            return result.json()
        else:
            return None
    except Exception as e:
        print(e)
        return None

def point_in_bounds(bounds, current_location):
    in_bounds = True
    for i in range(bounds.shape[0]-1):
        D = (bounds[i+1][0]-bounds[i][0])*(current_location[1]-bounds[i][1]) 
        - (current_location[0]-bounds[i][0])*(bounds[i+1][1]-bounds[i][1])
        if D < 0:
            in_bounds = False
    return in_bounds

async def termination_checks(ugv): # Run concurrently with main
    time_last_connected = time.time()
    time_elapsed_since_disconnect = time.time() - time_last_connected
    
    async for state in ugv.core.connection_state():
        if state.is_connected:
            time_last_connected = time.time()
            time_elapsed_since_disconnect = 0
        else:
            time_elapsed_since_disconnect = time.time() - time_last_connected
            
            await ugv.connect()
            
            print("Waiting for ugv to connect . . . ")
            async for state in ugv.core.connection_state():
                if state.is_connected:
                    print("Connected to ugv.")
                    break
        
        if time_elapsed_since_disconnect > 30:
            exit(1) # Terminate driving
        
        # TODO: Also terminate if out of bounds

async def run_ugv_mission():
    ugv = System()
    await ugv.connect()
    
    print("Waiting for ugv to connect . . . ")
    async for state in ugv.core.connection_state():
        if state.is_connected:
            print("Connected to ugv.")
            break
    

    post(SERVER_ROUTE+'/state', json= {"state": "STANDBY"})
    state = get(SERVER_ROUTE+'/state').json()['state']
    target_location = get(SERVER_ROUTE+'/mission').json()['ugvDrivePos']
    target_location = [target_location['latitude'], target_location['longitude'], 0, 0]
    drop_location_data = get(SERVER_ROUTE+'/mission').json()['airDropBoundaryPoints']
    drop_location_data_array = np.empty((len(drop_location_data)+1, 2))
    for i in range(len(drop_location_data)):
        drop_location_data_array[i] = np.array([drop_location_data[i]['latitude'], drop_location_data[i]['longitude']])
    drop_location_data_array[len(drop_location_data)] = drop_location_data_array[0]
    
    await asyncio.sleep(1)#420) # Sleep until takeoff guaranteed complete
    
    #get current_location

  
    while state != "COMPLETE":
        current_location = get_current_location(ugv)
        if state == "STANDBY":
            if (dist_to_ground() < DETACH_THRESH and point_in_bounds(drop_location_data_array, current_location)):
                detach_from_uas()
                post(SERVER_ROUTE+'/state', json= {"state": "DETACHED"})
                state = get(SERVER_ROUTE+'/state'.json()['state'])
                await ugv.action.arm()
                await ugv.action.takeoff()
                #await asyncio.sleep(10) # Don't drive while tumbling through air
                post(SERVER_ROUTE+'/state', json= {"state": "DRIVING"})
        elif state == "DRIVING":
            await ugv.action.goto_location(*target_location)
            post(SERVER_ROUTE+'/state', json= {"state": "COMPLETE"})
            #report_mission_success()
        state = get(SERVER_ROUTE+'/state'.json()['state'])
async def get_current_location(ugv):
    async for current_location in ugv.telemetry.position():
        data = [current_location.latitude_deg, current_location.longitude_deg, 0, 0]
        post(SERVER_ROUTE+'/heartbeat', json={"latitude":data[0], "longitude":data[1]})
        return data


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_ugv_mission())