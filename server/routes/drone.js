/*
* Routes for the drone to communicate with the intermediary server.
* Stores information about the drone.
*/

import express from 'express';

export default class Drone {
    constructor(interops_server) {
        this.router = express.Router();
        this.interops_server = interops_server;
        this.ground_station = undefined;

        this.current_mission = undefined;
        this.mission_index = 1;

        this.router.use((req, res, next) => {
            this.last_contact = Date.now();
            next();
        });

        // Check heartbeat
        this.router.get('/heartbeat', (res, req) => this.get_heartbeat_route(res, req));

        // Drone sends any drone updates, and server responds with any server updates
        this.router.post('/heartbeat', (res, req) => this.post_heartbeat_route(res, req));

        // Post telemetry data
        this.router.post('/telemetry', (res, req) => this.post_telemetry_route(res, req));

        // Get mission
        this.router.get('/mission', async (res, req) => await this.get_mission_route(res, req));

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
    }

    // Router functions

    get_heartbeat_route(req, res) {
        res.json({
            ground: Date.now(),
            interops: this.interops_server.connected
        });
    }

    post_heartbeat_route(req, res) {
        // Parse drone data
        let drone_data = req.body;

        // parse telemetry data
        let telemetry = drone_data.telemetryData;
        if (telemetry !== undefined)
            this.set_telemetry(telemetry);
        
        // Prepare server data to send to drone
        let ground_station_contact = undefined;
        
        if (this.ground_station !== undefined)
            ground_station_contact = this.ground_station.last_contact

        let server_data = {
            lastGroundContact: ground_station_contact,
            interopsConnected: this.interops_server.connected,
            currentMissionId: this.mission_index
        }
        res.status(200).json(server_data);
    }

    post_telemetry_route(req, res) { 
        let telemtry_data = req.body;
        this.set_telemetry(telemtry_data);

        if (this.interops_server.connected) {
            if (this.interops_server.post_telemetry(this.get_telemetry()))
                console.log("DEBUG: Posted telemtry data to Interops Server");
            else 
                console.log("DEBUG: Failed to post telemtry data to Interops Server");
        }
        res.status(200).send("Telemetry data saved");
    }

    async get_mission_route(req, res, id=-1) {
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
    }

    // Helper functions
    
    set_ground_station(station) {
        this.ground_station = station;
    }

    get_telemetry() {
        return {
            latitude: this.latitude,
            longitude: this.longitude,
            altitude: this.altitude,
            heading: this.heading,
        };
    }

    set_telemetry(telemetry) {
        if (telemetry.latitude !== undefined)
            this.latitude = telemetry.latitude;
        if (telemetry.longitude !== undefined)
            this.longitude = telemetry.longitude;
        if (telemetry.altitude !== undefined)
            this.altitude = telemetry.altitude;
        if (telemetry.heading !== undefined)
            this.heading = telemetry.heading;
    }
};