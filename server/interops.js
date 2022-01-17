/*
* This class encapsulates interaction with the interop server
*/

import fetch from "node-fetch"

export default class InteropServer {
    constructor (host) {
        this.host = host;
        this.connected = false;
        this.cookie = undefined;
    }

    async login(username, password) {
        return await fetch(`${this.host}/api/login`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        }).then(response => {
            if (!response.ok) {
                console.log(`Interops login failed: ${response.status} ${response.statusText}`);
                this.connected = false;
                this.cookie = undefined;
            }
            else {
                this.cookie = response.headers.get('Set-Cookie');
                this.connected = true;
            }
            return this.connected;
        }).catch(error => console.error('Error on Interops Login:', error));
    }

    async get_missions(index=1) {
        if (!this.connected) return undefined;

        return await fetch(`${this.host}/api/missions/${index}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Cookie': this.cookie
            }
        }).then(async response => {
            if (!response.ok)
                return undefined;
            else
                return await response.json();
        }).catch(error => console.error('Error on Interops Login:', error));
    }

    async post_telemetry(telemetry_data) {
        if (!this.connected) return false;

        return await fetch(`${this.host}/api/telemetry`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Cookie': this.cookie
            },
            body: JSON.stringify(telemetry_data)
        }).then(response => {
            return response.ok;
        }).catch(error => console.error('Error on Interops Login:', error));
    }
}