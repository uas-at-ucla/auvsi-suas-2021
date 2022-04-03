import React, { Component } from "react";
import dummy_map from "./images/dummy_map.jpg"

class EntireWindow extends Component {
    render(){
        return <div className="full_screen">
            <div className="odm-map">
                <img src={dummy_map} alt="dronemap"/>
            </div>
        </div>
    }
}


export default EntireWindow