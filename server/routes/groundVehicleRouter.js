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

        this.router.get('/state', async (req, res) => await this.get_state(req, res));

        this.router.post('/state', async (req, res) => await this.post_state(req, res));

        this.router.get('/heartbeat', async (req, res) => await this.get_heartbeat(req, res));

        this.router.post('/heartbeat', async (req, res) => await this.post_heartbeat(req, res));

        this.router.get('/mission', async (req, res) => await this.get_mission(req, res));
    }

    async post_state(req, res) {
        let data = req.body;
        this.ground_vehicle.set_state(data);
        res.status(200).send("DEBUG (UGV): UGV state saved");
    }

    async get_state(req, res) {
        res.status(200).send(this.ground_vehicle.get_state());
    }

    async post_heartbeat(req, res) {
        let data = req.body;
        this.ground_vehicle.set_telemetry(data);
        res.status(200).send("DEBUG (UGV): UGV telemetry data saved");
    }

    async get_heartbeat(req, res) {
        res.status(200).send(this.ground_vehicle.get_telemetry());
    }

    async get_mission(req, res) {

        if (this.interops_server.connected) {
            /** @todo: look into mission ID param */
            let mission = await this.interops_server.get_mission();

            if (mission != undefined) {
                // Parse the mission file so that we send back a more simplified JSON
                // Return the following:
                //      1. "airDropBoundaryPoints", which is a JSON Array
                //      2. "ugvDrivePos", which is a JSON
                //
                this.ground_vehicle.current_mission = {
                    "airDropBoundaryPoints": mission.airDropBoundaryPoints,
                    "ugvDrivePos": mission.ugvDrivePos
                };

                console.log("DEBUG (UGV): Got current mission data from Interops Server");

                // Return UGV mission
                res.status(200).json(this.ground_vehicle.current_mission);
            }
            else
            {
                console.log("DEBUG (UGV): Failed to get UGV mission from Interops Server");
                
                // Return ERROR status
                res.status(500);
            }
        }
        else
        {
            // Return ERROR status
            res.status(500);
        }
    }
}
