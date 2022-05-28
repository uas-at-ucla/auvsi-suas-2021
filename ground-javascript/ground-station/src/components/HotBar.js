import React, { useState, useEffect, useRef } from "react";
import BarMetric from './BarMetric.js'
import useInterval from './useInterval.js'
import axios from 'axios'
import "../styles/HotBar.css"
import { AiFillCar } from 'react-icons/ai'
import { GiDeliveryDrone } from 'react-icons/gi'

const serverAddress = "http://localhost:5000";
const POLL_INTERVAL = 3000;

function roundVal(val) {
    return Math.round((val + Number.EPSILON) * 100) / 100
}

function HotBar() {
    const [droneTelemetry, setDroneTelemetry] = useState({
        latitude: 0,
        longitude: 0,
        ground_velocity: 0,
        heading: 0,
        altitude: 0,
        battery: 0,
    })
    const [ugvTelemetry, setUgvTelemetry] = useState({
        latitude: 0,
        longitude: 0,
        altitude: 0,
        state: "STANDBY",
    })

    const getDroneTelemetry = () => {
        axios.get(serverAddress + "/ground/heartbeat").then((response) => {
            const telemetry = response.data.droneTelemetry
            setDroneTelemetry({
                latitude: roundVal(telemetry.latitude),
                longitude: roundVal(telemetry.longitude),
                ground_velocity: roundVal(telemetry.ground_velocity),
                heading: roundVal(telemetry.heading),
                altitude: roundVal(telemetry.altitude),
                battery: roundVal(telemetry.battery),
            })
        })
    }

    const getUgvTelemetry = () => {
        axios.get(serverAddress + "/ugv/heartbeat").then((response) => {
            const telemetry = response.data;
            setUgvTelemetry({
                latitude: telemetry.latitude,
                longitude: telemetry.latitude,
                altitude: telemetry.altitude,
                state: ugvTelemetry.state
            })
        })
        axios.get(serverAddress + "/ugv/state").then((response) => {
            const new_state = response.data.state;
            setUgvTelemetry({
                latitude: ugvTelemetry.latitude,
                longitude: ugvTelemetry.latitude,
                altitude: ugvTelemetry.altitude,
                state: new_state,
            })
        })
    }

    useInterval(async () => {
        getDroneTelemetry();
        getUgvTelemetry();
    }, POLL_INTERVAL)

    return(
        <div className="hot-bar-container">
            <div className="hot-bar-header">Telemetry</div>
            <div className = "vehicle-section">
                <div className="vehicle-header"><GiDeliveryDrone /></div>
                <BarMetric name="Latitude (°)" value={droneTelemetry.latitude} vehicle="drone"/>
                <BarMetric name="Longitude (°)" value={droneTelemetry.longitude} vehicle="drone"/>
                <BarMetric name="Heading (°N)" value={droneTelemetry.heading} vehicle="drone"/>
                <BarMetric name="Ground Speed (kts)" value={droneTelemetry.ground_velocity} vehicle="drone"/>
                <BarMetric name="Altitude (m)" value={droneTelemetry.altitude} vehicle="drone"/>
                <BarMetric name="Battery (%)" value={droneTelemetry.battery} vehicle="drone"/>
            </div>
            <div className="vehicle-section">
                <div className="vehicle-header"><AiFillCar /></div>
                <BarMetric name="Grounded" value={ugvTelemetry.state} vehicle="ugv"/>
                <BarMetric name="Latitude (°)" value={ugvTelemetry.latitude} vehicle="ugv"/>
                <BarMetric name="Longitude (°)" value={ugvTelemetry.longitude} vehicle="ugv"/>
            </div>
        </div>
    )
}

export default HotBar;