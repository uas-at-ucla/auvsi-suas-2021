import React, { Component } from "react";
import dummy_map from "./images/dummy_map.jpg"

import MapComponent from './Map.js'
import './EntireWindow.css';

class EntireWindow extends Component {
    render(){
        return <div className="full_screen">
            <div className="odm-map">
                <MapComponent />   
            </div>
        </div>
    }
}


export default EntireWindow