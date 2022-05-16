import asyncio, time
from mavsdk import System
from mavsdk import telemetry

END_STATE = 2
DETACH_THRESH = 1 # TODO

saved_location = [0, 0, 0, 0]

def dist_to_ground():
    return 0.5 # TEMP
    pass # TODO

def detach_from_uas():
    pass # TODO

def report_mission_sucess():
    pass # TODO

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

async def run_ugv_mission(target_location, drop_location, drop_bounds):
    ugv = System()
    await ugv.connect()
    
    print("Waiting for ugv to connect . . . ")
    async for state in ugv.core.connection_state():
        if state.is_connected:
            print("Connected to ugv.")
            break
    
    state = 0
    
    await asyncio.sleep(1)#420) # Sleep until takeoff guaranteed complete
    
    while state != END_STATE:
        current_location = await get_current_location(ugv)
        
        if state == 0:
            if (dist_to_ground() < DETACH_THRESH and 
            (abs(current_location[0] - drop_location[0] < drop_bounds) and 
            abs(current_location[1] - drop_location[1] < drop_bounds))):
                detach_from_uas()
                await ugv.action.arm()
                await ugv.action.takeoff()
                await asyncio.sleep(10) # Don't drive while tumbling through air
                state = 1
        elif state == 1:
            await ugv.action.goto_location(*target_location)
            state = 2
        elif state == 2:
            report_mission_success()

async def get_current_location(ugv):
    global saved_location
    data = []
    try:
        async for current_location in ugv.telemetry.position():
            data = [current_location.latitude_deg, current_location.longitude_deg, 0, 0]
            break;
    except:
        data = saved_location
    saved_location = data
    return data

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_ugv_mission([10, 20, 30, 40], [0, 0, 30, 0], .05))
