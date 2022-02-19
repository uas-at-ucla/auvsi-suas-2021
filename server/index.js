import express from 'express';
import cors from 'cors';
import { json } from 'express';
import InteropServer from './interops.js';
import 'dotenv/config'
import {Drone, GroundStation, GroundVehicle} from './data.js';

// Load in environment variables
const port = process.env.PORT || 3000
const interops_host = process.env.INTEROPS_HOST || "http://localhost:8000"
const username = process.env.INTEROPS_USERNAME || "testuser"
const password = process.env.INTEROPS_PASSWORD || "testpass"

const interops_server = new InteropServer(interops_host);

const app = express();
app.use(cors());
app.use(json());

app.get('/ping', (req, res) => {
    res.status(200).send("Pong!");
});

const state = {
    interops_server: interops_server,
    drone: new Drone(),
    ground_station: new GroundStation(),
    ground_vehicle: new GroundVehicle,
};

// Communication with the drone
import DroneRouter from './routes/droneRouter.js';
const drone = new DroneRouter(state);
app.use('/drone', drone.router);

// Communication with the ground station
import GroundStationRouter from './routes/groundStationRouter.js';
const ground = new GroundStationRouter(state);
app.use('/ground', ground.router);

// Communication with the ground vehicle
import GroundVehicleRouter from './routes/groundVehicleRouter.js';
const vehicle = new GroundVehicleRouter(state);
app.use('/ugv', vehicle.router);

app.listen(port, () => {
    // Login into Interops
    interops_server.login(username, password).then(async (success) => {
        if (success) console.log("Successfully logged into Interops Server");
        else console.log("Failed to log into Interops Server (interops functions will be disabled)");
    });

    console.log(`Intermediary Server running on port ${port}`);
});