import React, { useState } from "react";
import Map, { Marker } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";

const MAP_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || "";

export default function MapView({ userMarker, providers, intents, onMapClick }) {
  const [viewport, setViewport] = useState({
    latitude: 47.3769,
    longitude: 8.5417,
    zoom: 13,
  });

  if (!MAP_TOKEN) {
    return (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#e2e8f0",
          color: "#64748b",
        }}
      >
        Set REACT_APP_MAPBOX_TOKEN for the map.
      </div>
    );
  }

  return (
    <Map
      initialViewState={viewport}
      mapStyle="mapbox://styles/mapbox/streets-v11"
      mapboxAccessToken={MAP_TOKEN}
      style={{ width: "100%", height: "100%" }}
      onMove={(evt) => setViewport(evt.viewState)}
      onClick={(e) => onMapClick && onMapClick(e.lngLat)}
    >
      {providers &&
        providers.map((p) => (
          <Marker
            key={p.provider_id}
            longitude={p.lon}
            latitude={p.lat}
            anchor="center"
            onClick={(e) => e.originalEvent.stopPropagation()}
          >
            <div className="marker-provider" title={p.name} />
          </Marker>
        ))}
      {intents &&
        intents.map((i) => (
          <Marker
            key={i.intent_id}
            longitude={i.lon ?? i.longitude}
            latitude={i.lat ?? i.latitude}
            anchor="center"
          >
            <div className="marker-user" title={i.raw_text || i.text} />
          </Marker>
        ))}
      {userMarker && (
        <Marker
          longitude={userMarker.lon}
          latitude={userMarker.lat}
          anchor="center"
        >
          <div className="marker-user" title="you" />
        </Marker>
      )}
    </Map>
  );
}
