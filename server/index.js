import express from 'express';
import cors from 'cors';
import { json } from 'express';
import InteropServer from './interops.js';
import 'dotenv/config'

// Load in environment variables
const port = process.env.PORT || 3000
const interops_host = process.env.INTEROPS_HOST || "localhost:8000"
const username = process.env.INTEROPS_USERNAME || "testuser"
const password = process.env.INTEROPS_PASSWORD || "testpass"

const interops_server = new InteropServer(interops_host);

const app = express();
app.use(cors());
app.use(json());

app.get('/ping', (req, res) => {
    res.status(200).send("Pong!");
});

// Communication with the drone
import Drone from './routes/drone.js';
const drone = new Drone(interops_server);
app.use('/drone', drone.router);

// Communication with the ground station
import GroundStation from './routes/ground.js';
const ground = new GroundStation(interops_server);
app.use('/ground', ground.router);

drone.set_ground_station(ground);
ground.set_drone(drone);

app.listen(port, () => {
    // Login into Interops
    interops_server.login(username, password).then(async (success) => {
        if (success) console.log("Successfully logged into Interops Server");
        else console.log("Failed to log into Interops Server (interops functions will be disabled)");
    });

    console.log(`Intermediary Server running on port ${port}`);
});