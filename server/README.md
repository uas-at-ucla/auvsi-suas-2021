# Intermediary Server

This HTTP server acts as a middleman for the drone, ground station, and interops server.

```
             drone
               ^
               |
               v
ground <-->  server <--> interops
```

The server uses Express on NodeJs.

## Install and Config

To install nodejs and npm, run

```
curl -sL https://deb.nodesource.com/setup_16.x -o ~/nodesource_setup.sh
sudo bash ~/nodesource_setup.sh
sudo apt-get install nodejs
node -v
```

To install necessary packages, run

```
npm install
```

Create a file `.env` to store environment variables needed for configuration.

```
PORT=<port to host this server>
INTEROPS_HOST=<interops host address:port>
INTEROPS_USERNAME=<interops team username>
INTEROPS_PASSWORD=<interops team password>
```

Replace strings marked with \<description\> with config values.

**NOTE:** The servers some default values for config, see `index.js`.

## Start up

To start the server, run

```
npm start
```

On start up, the server will boot and login into the interops server.

In a separate bash terminal, you can test the server by running

```
curl localhost:3000/ping
```

Replace 3000 with whatever port number is set in the `.env` file.

The server should reply with *Pong!*.

# API

The API and JSON format are similar to the interops specifications.

## /drone

routes which the drone should use.

### POST /drone/telemetry

saves the posted drone telemtry data.

```
{
  "latitude": <drone latitude>
  "longitude": <drone longitude>
  "altitude": <drone altitude>
  "heading": <drone heading>
}
```

### POST /drone/heartbeat

Used for more advanced heartbeat with the server

Send

```
{
  "telemetryData": {
    "latitude": <drone latitude>
    "longitude": <drone longitude>
    "altitude": <drone altitude>
    "heading": <drone heading>
  }
}
```

Receive

```
{
  "lastGroundContact": <UTC timestamp when ground station last contacted server>
  "interopsConnected": <whether server is still connected to interops>
  "currentMissionId": <mission id currently stored in server>
}
```

### GET /drone/mission

Gets the current mission (see interops server for mission data structure)

### GET /drone/mission/:id

Get the mission with specified id (see interops server for mission data structure)

### GET /drone/ugvtelemetry

Get ugv telemetry for the drone

## /ground

routes which the ground station should use.

### GET /ground/heartbeat

Simple heartbeat to server from ground station

Returns 

```
{
  "latitude": <last know drone latitude>
  "longitude": <last know drone longitude>
  "altitude": <last know drone altitude>
  "heading": <last know drone heading>
}
```

### GET /ground/mission

Gets the current mission (see interops server for mission data structure)

## /ugv

routes which the UGV should use.

### GET /ugv/state

Get the last updated UGV state.

- "STANDBY" = UGV does nothing (i.e. hanging there).

- "LOWERING" = Drone is lowering the UGV.

- "DETACHED" = Drone is detached from UGV.

- "DRIVING" = UGV is driving.

- "COMPLETE" = UGV accomplished it's mission.

Example response:

```json
{
  "state": "STANDBY"
}
```

### POST /ugv/state

Update the UGV state.

- "STANDBY" = UGV does nothing (i.e. hanging there).

- "LOWERING" = Drone is lowering the UGV.

- "DETACHED" = Drone is detached from UGV.

- "DRIVING" = UGV is driving.

- "COMPLETE" = UGV accomplished it's mission.

Example POST JSON:

```json
{
  "state": "STANDBY"
}
```

### GET /ugv/heartbeat

Get the last updated UGV telemetry.

Example response:

```json
{
  "latitude": 10,
  "longitude": 15,
  "altitude": 100
}
```

### POST /ugv/heartbeat

Updates the server with the current UGV's telemetry.

POST JSON Format:

```json
{
  "latitude": 10,
  "longitude": 15,
  "altitude": 100
}
```

### GET /ugv/mission

Gets the current ugv mission data.

**If unsuccessful,** return status `500`, meaning the intermediary server incountered an internal error.

**If successful,** returns status `200` and a JSON in the following format:

```json
{
  "airDropBoundaryPoints": [
    {
      "latitude": 38.14616666666666,
      "longitude": -76.42666666666668
    },
    {
      "latitude": 38.14636111111111,
      "longitude": -76.42616666666667
    },
    {
      "latitude": 38.14558333333334,
      "longitude": -76.42608333333334
    },
    {
      "latitude": 38.14541666666667,
      "longitude": -76.42661111111111
    }
  ],
  "ugvDrivePos": {
    "latitude": 38.146152,
    "longitude": -76.426396
  }
}
```