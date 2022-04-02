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

class GroundVelocity {
    north_m_s;
    east_m_s;
    down_m_s;

    constructor(north_m_s, east_m_s, down_m_s) {
        this.north_m_s = north_m_s;
        this.east_m_s = east_m_s;
        this.down_m_s = down_m_s;
    }
}

class AngularVelocity {
    roll_rad_s;
    pitch_rad_s;
    yaw_rad_s;

    constructor(roll_rad_s, pitch_rad_s, yaw_rad_s) {
        this.roll_rad_s = roll_rad_s;
        this.pitch_rad_s = pitch_rad_s;
        this.yaw_rad_s = yaw_rad_s;
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
        
        // Most likely will be none as drone code
        // does not send anything
        this.is_in_air = data.is_in_air;
        this.is_landed = data.is_landed;

        this.roll = data.roll;
        this.pitch = data.pitch;
        this.yaw = data.yaw;
        this.g_velocity = new GroundVelocity(data.g_velocity.north_m_s, data.g_velocity.east_m_s, data.g_velocity.down_m_s)
        this.a_velocity = new AngularVelocity(data.a_velocity.roll_rad_s, data.a_velocity.pitch_rad_s, data.a_velocity.yaw_rad_s)
        this.forward = data.forward;
        this.right = data.right;
        this.down = data.down;
        this.battery = data.battery;

        console.log(this.get_telemetry());
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