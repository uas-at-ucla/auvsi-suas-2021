import asyncio, time
from mavsdk import System

END_STATE = 2
DETACH_THRESH = 1 # TODO

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
    
    async for state in ugv.core.connectoin_state():
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

async def run_ugv_mission(target_location):
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
        if state == 0:
            if (dist_to_ground() < DETACH_THRESH):
                detach_from_uas()
                await ugv.action.arm()
                await ugv.action.takeoff()
                state = 1
        elif state == 1:
            await asyncio.sleep(10) # Don't drive while tumbling through air
            await ugv.action.goto_location(*target_location)
            state = 2
        elif state == 2:
            report_mission_success()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_ugv_mission([10, 20, 30, 40]))
