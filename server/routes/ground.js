/*
* Routes for the ground station to communicate with the intermediary server.
*/

import express from 'express';

export default class GroundStation {
    constructor(interops_server) {
        this.router = express.Router();
        this.interops_server = interops_server;
        this.drone = undefined;

        this.router.use((req, res, next) => {
            this.last_contact = Date.now();
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
        res.json(this.drone.get_telemetry());
        res.status(200).end();
    }

    // Helper methods

    set_drone(drone) {
        this.drone = drone;
    }
};