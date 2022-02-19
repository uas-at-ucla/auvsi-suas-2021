/*
* Routes for the ground station to communicate with the intermediary server.
*/

import express from 'express';

export default class GroundStationRouter {
    constructor(state) {
        this.router = express.Router();
        
        this.interops_server = state.interops_server;
        this.drone = state.drone;
        this.ground_station = state.ground_station;
        this.ground_vehicle = state.ground_vehicle;

        this.router.use((req, res, next) => {
            this.ground_station.last_contact = Date.now();
            next();
        });

        this.router.get('/heartbeat', (req, res) => this.get_heartbeat(req, res));

        this.router.get('/mission', async (req, res) => {
            if (this.drone !== undefined && this.drone.current_mission !== undefined)
                res.json(this.drone.current_mission)
            else if (this.interops_server.connected)
                res.json(await this.interops_server.get_mission())
            else
                res.status(200).end()
        });
    }

    // Router methods

    get_heartbeat(req, res) {
        res.json({
            lastDroneContact: this.drone.last_contact,
            droneTelemetry: this.drone.get_telemetry(),
        });
        res.status(200).end();
    }
};