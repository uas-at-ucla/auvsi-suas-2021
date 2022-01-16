# Intermediary Server
This server acts as a middleman for the drone, ground station, and interops server.
```
             drone
               ^
               |
               v
ground <-->  server <--> interops
```
The server uses Express on NodeJs

## Install and Config
To install necessary packages, run
```
npm install
```

Create a file `.env` to store environment variables needed for configuration
```
INTEROPS_HOST=<interops host address:port>
USERNAME=<interops team username>
PASSWORD=<interops team password>
```
Replace strings marked with \<description\> with config values

## Start up
To start the server, run
```
npm start
```

On start up, the server will boot and login into the interops server

## API
The API and JSON format are similar to the interops specifications
