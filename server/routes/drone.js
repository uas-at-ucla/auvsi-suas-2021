/*
* Routes for the drone to communicate with the intermediary server.
* Stores information about the drone.
*/

import express from 'express';

export default class Drone {
    constructor(interops_server) {
        this.router = express.Router();
        this.interops_server = interops_server;
        this.current_mission = undefined;
        this.mission_index = 1;

        this.router.use((req, res, next) => {
            this.last_contact = Date.now();
            next();
        });

        // Check heartbeat
        this.router.get('/heartbeat', (req, res) => {
            res.json({
                ground: new Date.now(),
                interops: this.interops_server.connected
            });
        });

        // Post telemetry data
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
            // console.log(`DEBUG: telemetry data ${this.get_telemetry()}`);
            res.status(200).send("Telemetry data saved");
        });

        // Get mission
        this.router.get('/mission', async (req, res) => {
            if (this.interops_server.connected) {
                let mission = await this.interops_server.get_mission(this.mission_index);
                //console.log(mission);
                if (mission) {
                    this.current_mission = mission;
                    console.log("DEBUG: Got current mission data from Interops Server");
                }
                else if (mission === undefined) {
                    console.log("DEBUG: Failed to get telemtry from Interops Server");
                }
            }
            res.status(200).json(this.current_mission);
        });

        this.router.get('/mission/:id', async (req, res) => {
            let index = parseInt(req.params.index, 10);
            if (this.interops_server.connected) {
                let mission = await this.interops_server.get_mission(index);
                //console.log(mission);
                if (mission) {
                    console.log("DEBUG: Got current mission data from Interops Server");
                    res.status(200).json(mission);
                    return;
                }
                else if (mission === undefined) {
                    console.log("DEBUG: Failed to get telemtry from Interops Server");
                }
            }
            res.status(404).send("Could not get mission data from Interops Server");
        });

        // Finish mission
        this.router.post('/mission', (req, res) => {
            let confirmation = req.body;
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