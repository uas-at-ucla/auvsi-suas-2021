import React from "react";
import "../styles/BarMetric.css"

function BarMetric({name, value, vehicle}) {
    return (
        <div className={`metric ${vehicle}`}>
            <span className="metricName">{name}</span> 
            <span className="metricValue">{value}</span>
        </div>
    )
}

export default BarMetric;