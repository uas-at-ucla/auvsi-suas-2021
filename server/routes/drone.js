/*
* Routes for the drone to communicate with the intermediary server.
* Stores information about the drone.
*/

import express from 'express';

export default class Drone {
    constructor(interops_server) {
        this.router = express.Router();
        this.interops_server = interops_server;

        this.router.use((req, res, next) => {
            this.last_contact = Date.now();
            next();
        });

        this.router.post('/telemetry', (req, res) => {
            let telemtry_data = req.body;
            this.latitude = telemtry_data.latitude;
            this.longitude = telemtry_data.longitude;
            this.altitude = telemtry_data.altitude;
            this.heading = telemtry_data.heading;

            if (this.interops_server.connected) {
                if (this.interops_server.post_telemetry(this.get_telemetry()))
                    console.log("DEBUG: Posted telemtry data to Interops Server");
                else 
                    console.log("DEBUG: Failed to post telemtry data to Interops Server");
            }

            res.status(200).send("Telemetry data saved");
        });
    }

    get_telemetry() {
        return {
            latitude: this.latitude,
            longitude: this.longitude,
            altitude: this.altitude,
            heading: this.heading,
        };
    }
};