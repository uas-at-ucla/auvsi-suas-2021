import React, { Component } from "react";
import dummy_map from "../images/dummy_map.jpg"
import "../styles/MapSide.css"

function MapSide() {
    return(
        <div className="map-side-container">
            <img className="map" src={dummy_map} alt="dronemap"/>
        </div>
    )
}

export default MapSide;