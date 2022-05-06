import React, { useState } from "react";
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
                <div className="metric">
                    <span className="metricName">Latitude</span> 
                    <span className="metricValue">{latitude}°</span>
                </div>
                <div className="metric">
                    <span className="metricName">Longitude</span> 
                    <span className="metricValue">{longitude}°</span>
                </div>
                <div className="metric">
                    <span className="metricName">Airspeed</span>
                    <span className="metricValue">{airSpeed} knots</span>
                </div>
                <div className="metric">
                    <span className="metricName">Ground Speed</span>
                    <span className="metricValue">{airSpeed + windSpeed} knots</span>
                </div>
                <div className="metric">
                    <span className="metricName">Altitude</span>
                    <span className="metricValue">{altitude}m</span>
                </div>
            </div>
            <div className="vehicle-section">
                <div className="hot-bar-header">UGV Telemetry</div>
                <div className="metric">
                    <span className="metricName">Direction</span>
                    <span className="metricValue">{ugvDir} °N</span>
                </div>
                <div className="metric">
                    <span className="metricName">Speed</span>
                    <span className="metricValue">{ugvSpeed} m/s</span>
                </div>
            </div>
        </div>
    )
}

export default HotBar;