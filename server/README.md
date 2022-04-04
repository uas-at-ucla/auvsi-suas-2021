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

### POST /ugv/heartbeat
Updates the server with the current UGV's telemetry

### GET /ugv/mission
Gets the current ugv mission data.