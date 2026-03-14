import React, { useState, useEffect } from "react";
import MapView from "./components/MapView";
import IntentComposer from "./components/IntentComposer";
import ProviderDashboard from "./components/ProviderDashboard";
import { createSocket } from "./utils/socket";
import { useDemoSetup } from "./demo/demoSetup";

function App() {
  const [mode, setMode] = useState("user");
  const [userLocation, setUserLocation] = useState({ lat: 47.3769, lon: 8.5417 });
  const [providers, setProviders] = useState([]);
  const [intents, setIntents] = useState([]);
  const [providerProfile, setProviderProfile] = useState(null);

  useDemoSetup({ setProviders, setIntents, setProviderProfile });

  useEffect(function () {
    var WS_BASE = process.env.REACT_APP_WS_BASE;
    if (!WS_BASE) return;
    var socket = createSocket(WS_BASE + "/events", function (msg) {
      if (msg.type === "intent.created") setIntents(function (s) { return [msg.payload].concat(s); });
      if (msg.type === "bid.submitted") console.log("bid", msg.payload);
    });
    return function () { socket && socket.close(); };
  }, []);

  return (
    <div className="app">
      <div className="mapColumn">
        <MapView
          userMarker={userLocation}
          providers={providers}
          intents={intents}
          onMapClick={function (lngLat) {
            setUserLocation({ lat: lngLat.lat, lon: lngLat.lng });
          }}
        />
      </div>
      <div className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <div className="logo">DV</div>
            <div>
              <h3 className="h2">Dynamic Vector</h3>
              <div className="small">Broadcast intent — let nearby merchants bid</div>
            </div>
          </div>
          <div>
            <select value={mode} onChange={function (e) { setMode(e.target.value); }}>
              <option value="user">User</option>
              <option value="provider">Provider</option>
            </select>
          </div>
        </div>

        {mode === "user" && (
          <>
            <IntentComposer
              userLocation={userLocation}
              onCreated={function (id) { alert("Intent sent: " + id); }}
            />
            <div style={{ marginTop: 12 }}>
              <h4 style={{ margin: "8px 0" }}>Active bids / offers</h4>
              <div className="small">(In demo mode, bids appear below when provider responds)</div>
              <div id="offers"></div>
            </div>
          </>
        )}

        {mode === "provider" && providerProfile && (
          <ProviderDashboard provider={providerProfile} />
        )}

        <div style={{ marginTop: 16 }}>
          <h4>Providers (demo)</h4>
          {providers.map(function (p) {
            return (
              <div key={p.provider_id} className="card">
                {p.name} — {(p.categories || []).join(", ")}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default App;
