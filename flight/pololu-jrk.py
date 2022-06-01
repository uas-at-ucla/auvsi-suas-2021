# NOTE: If you have multiple Jrk G2 devices, you need to specify the serial number.
#       To get the serial number, run "jrk2cmd --list"
#
# NOTE: All functions that will cause the JRK to rotate the motor will due so at full
#       duty cycle.
#       
#       (05-20-22) - We are using high-torque motors requiring 12V to 24V of input.
#
# NOTE: The Jrk's input mode must be "Serial / I2C / USB".
import sys
import logging
import subprocess
import yaml

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)
 
# Base command
def jrk2cmd(*args):
    # Crude check that jrk2cmd is installed
    try:
        if "Usage" not in subprocess.check_output('jrk2cmd').decode('ascii'):
            raise Exception()
        log.info("jrk2cmd installation identified")
    except:
        log.error("jrk2cmd not set up")
        raise SystemError("jrk2cmd not set up")

    if check_jrk_connection() == False:
        log.error("Cannot find JRK")
        raise SystemError("Cannot find JRK")
    log.info("JRK connected")

    return subprocess.check_output(['jrk2cmd'] + list(args))

# Returns True if a JRK device is connected. False otherwise.
def check_jrk_connection():
    try:
        # Get current status of JRK connection
        status = subprocess.check_output(['jrk2cmd', '-s', '--full']).decode('ascii')
        
        if "Error: No device was found." in status:
            return False

        return True
    except Exception as e:
        return False

# Lowers the UGV
def lower():
    """
    "https://www.pololu.com/docs/pdf/0J73/jrk_g2_motor_controller.pdf"
    
    Passage from documentation (Section 5.1):

    "When the “Feedback mode” is “None”, the Jrk calculates its “Duty cycle target”
    variable by simply subtracting 2048 from the “Target” variable. So a target of 
    2048 corresponds to the motor being off, while a target of 2648 corresponds to 
    full speed forward (100%), and a target of 1448 corresponds to full speed reverse 
    (−100%)."

    """

    # Stop the motor before switching directions
    stop()

    lower_target = 2648
    yaml.safe_load(jrk2cmd('--target', str(lower_target), '--run'))

# Raises the UGV
def bring_up():
    # NOTE: Cannot use "raise" as function name as it is a reserved keyword.
    """
    "https://www.pololu.com/docs/pdf/0J73/jrk_g2_motor_controller.pdf"
    
    Passage from documentation (Section 5.1):

    "When the “Feedback mode” is “None”, the Jrk calculates its “Duty cycle target”
    variable by simply subtracting 2048 from the “Target” variable. So a target of 
    2048 corresponds to the motor being off, while a target of 2648 corresponds to 
    full speed forward (100%), and a target of 1448 corresponds to full speed reverse 
    (−100%)."

    """
    
    # Stop the motor before switching directions
    stop()

    bring_up_target = 1448
    yaml.safe_load(jrk2cmd('--target', str(bring_up_target), '--run'))

# Set a target motor value
def set_target(target: int):

    # target == 1448 means -100%
    # target == 2648 means +100%
    if target >= 1448 and target <= 2648:
        # Stop the motor before switching directions
        stop()

        # Set the target
        yaml.safe_load(jrk2cmd('--target', str(target), '--run'))
    else:
        stop()
        raise Exception('Target out of range for JRK')
    

# Stops raising/lowering
def stop():
    yaml.safe_load(jrk2cmd('--stop'))



import time
if __name__ == "__main__":
    set_target(20000)