class Position {
    latitude;
    longitude;
    absolute_altitude;
    relative_altitude;

    constructor(latitude, longitude, absolute_altitude, relative_altitude) {
        this.latitude = latitude;
        this.longitude = longitude;
        this.absolute_altitude = absolute_altitude;
        this.relative_altitude = relative_altitude;
    }
}

class Drone {
    last_contact;
    current_mission;

    // TELEMETRY DATA
    position = new Position(undefined, undefined, undefined, undefined); // lat, long, abs alt, rel alt
    heading;    // Drone heading
    is_in_air;  // Enum for whether drone is in air
    is_landed;  // Enum for landing status
    roll;
    pitch;
    yaw;
    g_velocity; // Ground velocity
    a_velocity; // Angular velocity
    forward;    // Forward acceleration
    right;      // Right acceleration
    down;       // Down acceleration
    
    battery;

    set_telemetry(data) {
        this.position = new Position(
            data.latitude,
            data.longitude,
            data.absolute_altitude,
            data.relative_altitude
        );
        this.heading = data.heading;
        
        // this.is_in_air = null;
        // this.is_landed = null;

        this.roll = data.roll;
        this.pitch = data.pitch;
        this.yaw = data.yaw;
        this.g_velocity = data.g_velocity;
        this.a_velocity = data.a_velocity;
        this.forward = data.forward;
        this.right = data.right;
        this.down = data.down;
        this.battery = data.battery;

        console.log(data);
    }

    get_telemetry() {
        return {
            latitude: this.position.latitude,
            longitude: this.position.longitude,
            absolute_altitude: this.position.absolute_altitude,
            relative_altitude: this.position.relative_altitude,
            heading: this.heading,
            roll: this.roll,
            pitch: this.pitch,
            yaw: this.yaw,
            ground_velocity: this.g_velocity,
            angular_velocity: this.a_velocity,
            forward_acceleration: this.forward,
            right_acceleration: this.right,
            down_acceleration: this.down,
            battery: this.battery
        }
    }

    get_mission_id() {
        if (this.current_mission !== undefined)
            return this.current_mission.id;
        else
            return undefined;
    }
}

class GroundStation {
    last_contact;
}

class GroundVehicle {
    last_contact;
    position = new Position(undefined, undefined, undefined);
    grounded = false;

    set_telemetry(data) {
        this.position = new Position(
            data.latitude,
            data.longitude,
            data.altitude
        );
        this.grounded = data.isGrounded;
    }

    get_telemetry() {
        return {
            latitude: this.position.latitude,
            longitude: this.position.longitude,
            altitude: this.position.absolute_altitude,
            isGrounded: this.grounded
        }
    }
}

export { Drone, GroundStation, GroundVehicle, Position };