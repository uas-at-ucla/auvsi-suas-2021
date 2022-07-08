import React, { useState } from "react";
import BarMetric from './BarMetric.js'
import "../styles/HotBar.css"

function HotBar() {
    const [latitude, setLatitude] = useState(0)
    const [longitude, setLongitude] = useState(0)
    const [airSpeed, setAirSpeed] = useState(0)
    const [windSpeed, setWindSpeed] = useState(0)
    const [altitude, setAltitude] = useState(0)
    const [ugvDir, SetUgvDir] = useState(0)
    const [ugvSpeed, SetUgvSpeed] = useState(0)

    return(
        <div className="hot-bar-container">
            <div className = "vehicle-section">
                <div className="hot-bar-header">Drone Telemetry</div>
                <BarMetric name="Latitude" valString={`${latitude}°`}/>
                <BarMetric name="Longitude" valString={`${longitude}°`}/>
                <BarMetric name="Airspeed" valString={`${airSpeed} knots`}/>
                <BarMetric name="Ground Speed" valString={`${airSpeed + windSpeed} knots`}/>
                <BarMetric name="Altitude" valString={`${altitude}m`}/>
            </div>
            <div className="vehicle-section">
                <div className="hot-bar-header">UGV Telemetry</div>
                <BarMetric name="Direction" valString={`${ugvDir} °N`}/>
                <BarMetric name="Speed" valString={`${ugvSpeed} m/s`}/>
            </div>
        </div>
    )
}

export default HotBar;