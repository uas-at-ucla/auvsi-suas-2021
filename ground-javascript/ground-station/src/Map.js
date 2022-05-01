import React, { useState, useRef, useEffect } from 'react';

import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import OSM from 'ol/source/OSM'
import { fromLonLat } from 'ol/proj';

export default function MapComponent(props) {

    // state and ref setting logic eliminated for brevity
    // set intial state - used to track references to OpenLayers 
    //  objects for use in hooks, event handlers, etc.
    const [map, setMap] = useState()
    const [featuresLayer, setFeaturesLayer] = useState()
    const [selectedCoord, setSelectedCoord] = useState()

    // get ref to div element - OpenLayers will render into this div
    const mapElement = useRef()

    // initialize map on first render - logic formerly put into componentDidMount
    useEffect(() => {
        // create and add vector source layer
        // const initalFeaturesLayer = new VectorLayer({
        //     source: new VectorSource()
        // })

        // create map
        const initialMap = new Map({
            target: mapElement.current,
            layers: [
                new TileLayer({
                    source: new OSM()
                }),
                //initalFeaturesLayer
            ],
            view: new View({
                projection: 'EPSG:900913',
                center: fromLonLat([-118.4421593056627, 34.070968197472176], 'EPSG:900913'),
                //projection: fromLonLat([34.070958199405275, -118.44218478664628]),
                zoom: 20
            }),
            controls: []
        })

        // save map and vector layer references to state
        setMap(initialMap)
        //setFeaturesLayer(initalFeaturesLayer)
    }, [])

    // return/render logic eliminated for brevity
    return (
        <div ref={mapElement} className="map-container" style={{height: '1000px', width: '1000px'}}/>
    )
}