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
            this.last_contact = Data.now();
            next();
        });

        this.router.get('/heartbeat', this.get_heartbeat);

        this.router.get('/mission', (req, res) => {
            if (this.interops_server.connected)
                res.json(this.interops_server.get_mission)
            else {
                res.json({
                    id: 1,
                    waypoints: [
                        {
                            latitude: 100,
                            longitude: 100,
                        },
                        {
                            latitude: 200,
                            longitude: 200,
                        },
                    ]
                });
            }
            res.status(200).end();
        });

        this.router.post('/test', (req, res) => {
            console.log(req.body);
            res.send(req.body);
        });
    }

    // Router methods

    get_heartbeat(req, res) {
        if (this.drone !== undefined)
            res.json(drone.get_telemetry());

        res.status(200).end();
    }

    // Helper methods

    set_drone(drone) {
        this.drone = drone;
    }
};