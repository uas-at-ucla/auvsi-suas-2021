import React from "react";
import "../styles/BarMetric.css"

function BarMetric({name, valString}) {
    return (
        <div className="metric">
            <span className="metricName">{name}</span> 
            <span className="metricValue">{valString}</span>
        </div>
    )
}

export default BarMetric;