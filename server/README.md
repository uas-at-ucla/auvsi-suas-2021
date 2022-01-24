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
Content-Type: application/json

{
    latitude: <drone latitude>
    longitude: <drone longitude>
    altitude: <drone altitude>
    heading: <drone heading>
}
```

### GET /drone/mission
Gets the current mission (see interops server for mission data structure)

### GET /drone/mission/:id
Get the mission with specified id (see interops server for mission data structure)

## /ground
routes which the ground station should use.