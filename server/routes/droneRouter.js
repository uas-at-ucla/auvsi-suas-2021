/*
* Routes for the drone to communicate with the intermediary server.
*/

import express from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';

export default class DroneRouter {
    constructor(state) {
        this.router = express.Router();

        this.interops_server = state.interops_server;
        this.drone = state.drone;
        this.ground_station = state.ground_station;
        this.ground_vehicle = state.ground_vehicle;

        this.upload = multer({
            dest: "./images/"
        })

        this.router.use((req, res, next) => {
            this.drone.last_contact = Date.now();
            next();
        });

        // Drone sends any drone updates, and server responds with any server updates
        this.router.post('/heartbeat', (req, res) => this.post_heartbeat(req, res));

        // Post telemetry data
        this.router.post('/telemetry', (req, res) => this.post_telemetry(req, res));

        // Get mission
        this.router.get('/mission', async (req, res) => await this.get_mission(req, res));

        // Get ugv telemtry
        this.router.get('/ugvtelemetry', (req, res) => this.get_ugv_telemetry(req, res));


        /** @todo check if this is needed */
        // this.router.get('/mission/:id', async (req, res) => {
        //     let index = parseInt(req.params.index, 10);
        //     if (this.interops_server.connected) {
        //         let mission = await this.interops_server.get_mission(index);
        //         //console.log(mission);
        //         if (mission) {
        //             console.log("DEBUG: Got current mission data from Interops Server");
        //             this.drone.mission = mission;
        //             res.status(200).json(mission);
        //             return;
        //         }
        //         else if (mission === undefined) {
        //             console.log("DEBUG: Failed to get telemtry from Interops Server");
        //         }
        //     }
        //     res.status(404).send("Could not get mission data from Interops Server");
        // });

        this.router.post('/upload_odm_image',  this.upload.single("image"), async (req, res) => {
            let type = req.file.mimetype;
            let dest = req.file.destination;
            let filename = path.join(dest, req.file.filename);
            let originalname = path.join(dest, req.file.originalname);

            if (!["image/jpg", "image/jpeg"].includes(type)) {
                res.status(403).send("Invalid File Format");
                fs.unlinkSync(filename);
                return;
            }

            fs.renameSync(filename, originalname);
            res.status(200).send("Uploaded Successfully");
        });
    }

    // Router functions
    post_heartbeat(req, res) {
        // Parse drone data
        let drone_data = req.body;

        // parse telemetry data
        let telemetry = drone_data.telemetryData;
        if (telemetry !== undefined)
            this.drone.set_telemetry(telemetry);
        
        // Prepare server data to send to drone
        let ground_station_contact = this.ground_station.last_contact;

        let server_data = {
            lastGroundStationContact: ground_station_contact,
            interopsConnected: this.interops_server.connected,
            currentMissionId: this.drone.get_mission_id(),
        }
        res.status(200).json(server_data);
    }

    post_telemetry(req, res) { 
        let telemtry_data = req.body;
        this.drone.set_telemetry(telemtry_data);

        if (this.interops_server.connected) {
            if (this.interops_server.post_telemetry(this.get_telemetry()))
                console.log("DEBUG: Posted telemtry data to Interops Server");
            else 
                console.log("DEBUG: Failed to post telemtry data to Interops Server");
        }
        res.status(200).send("Telemetry data saved");
    }

    async get_mission(req, res, id=-1) {
        if (this.interops_server.connected) {
            let mission = await this.interops_server.get_mission(1); // TODO: check how to get correct mission id
            //console.log(mission);
            if (mission) {
                this.drone.current_mission = mission;
                console.log("DEBUG: Got current mission data from Interops Server");
            }
            else if (mission === undefined) {
                console.log("DEBUG: Failed to get telemtry from Interops Server");
            }
        }
        // console.log(this.drone.get_mission_id())
        res.status(200).json(this.drone.current_mission);
    }

    get_ugv_telemetry(req, res) {
        res.status(200).json(this.ground_vehicle.get_telemetry())
    }
};