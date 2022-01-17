/*
* Routes for the ground station to communicate with the intermediary server.
*/

import express from 'express';

export default class GroundStation {
    constructor(interops_server) {
        this.router = express.Router();
        this.interops_server = interops_server;
    }
};