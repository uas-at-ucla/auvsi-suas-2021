/*
* Routes for the ground vehicle to communicate with the intermediary server.
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
            this.ground_vehicle.last_contact = Date.now();
            next();
        });

        this.router.post('/heartbeat', async (req, res) => await this.post_heartbeat(req, res));

        this.router.get('/mission', async (req, res) => await this.get_mission(req, res));
    }

    async post_heartbeat(req, res) {
        let data = req.body;
        this.ground_vehicle.set_telemetry(data);
        res.status(200).send("Telemetry data saved");
    }

    async get_mission(req, res) {
        res.status(501).send("Not Implemented");
    }
}