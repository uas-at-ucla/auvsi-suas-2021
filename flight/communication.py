"""
Module for communicating with the Intermediary Server
"""
from datetime import datetime
import requests
from decouple import config

HOST = config("HOST", default="http://localhost:3000")

heartbeat_established = False
last_heartbeat = datetime.now()


def test_connection():
    try:
        result = requests.get(f"{HOST}/ping")
        return result.ok
    except:
        return False


async def post_heartbeat(drone):
    # NOTE: Did not include is_in_air or is_landed because may not be
    #       necessary
    try:
        result = requests.post(f"{HOST}/drone/heartbeat", json={
            "telemetryData": {
                "latitude": drone.telemetry.latitude,
                "longitude": drone.telemetry.longitude,
                "absolute_altitude": drone.telemetry.absolute_altitude,
                "relative_altitude": drone.telemetry.relative_altitude,
                "heading": drone.telemetry.yaw,
                "is_in_air": drone.telemetry.is_in_air,
                # "is_landed": drone.telemetry.is_landed,  # Enum
                "roll": drone.telemetry.roll,
                "pitch": drone.telemetry.pitch,
                "yaw": drone.telemetry.yaw,
                "ground_velocity": {
                    "north_kn": drone.telemetry.ground_velocity.north_kn,
                    "east_kn": drone.telemetry.ground_velocity.east_kn,
                    "down_kn": drone.telemetry.ground_velocity.down_kn,
                } if drone.telemetry.ground_velocity is not None else None,
                "angular_velocity": {
                    "roll_rad_s": drone.telemetry.angular_velocity.roll_rad_s,
                    "pitch_rad_s": drone.telemetry.angular_velocity.pitch_rad_s,
                    "yaw_rad_s": drone.telemetry.angular_velocity.yaw_rad_s
                } if drone.telemetry.angular_velocity is not None else None,
                "forward": drone.telemetry.forward,
                "right": drone.telemetry.right,
                "down": drone.telemetry.down,
                "battery": drone.telemetry.battery_remaining
            }
        })

        if (result.ok):
            return result.json()
        else:
            return None
    except Exception as e:
        print(e)
        return None


async def get_mission():
    try:
        result = requests.get(f"{HOST}/drone/mission")
        if (result.ok):
            return result.json()
        else:
            return None
    except Exception as e:
        print(e)
        return None

async def post_image(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            result = requests.post(f"{HOST}/drone/upload_odm_image", files={'upload_file': img_file})
        if (result.ok):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False