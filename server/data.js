class Position {
    latitude;
    longitude;
    altitude;

    constructor(latitude, longitude, altitude) {
        this.latitude = latitude;
        this.longitude = longitude;
        this.altitude = altitude;
    }
}

class Drone {
    last_contact;
    position = new Position(undefined, undefined, undefined);
    heading;
    current_mission;

    set_telemetry(data) {
        this.position = new Position(
            data.latitude,
            data.longitude,
            data.altitude
        );
        this.heading = data.heading;
    }

    get_telemetry() {
        return {
            latitude: this.position.latitude,
            longitude: this.position.longitude,
            altitude: this.position.altitude,
            heading: this.heading
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
            altitude: this.position.altitude,
            isGrounded: this.grounded
        }
    }
}

export { Drone, GroundStation, GroundVehicle, Position };