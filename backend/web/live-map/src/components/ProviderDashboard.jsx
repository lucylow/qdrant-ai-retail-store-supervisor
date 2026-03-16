import React, { useState, useEffect } from "react";
import { submitBid } from "../api";

export default function ProviderDashboard({ provider }) {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    function onMsg(e) {
      if (e.type === "intent.created") {
        const intent = e.payload;
        const lon = intent.lon ?? intent.longitude;
        const lat = intent.lat ?? intent.latitude;
        const dlon = (lon - provider.lon) * 111000 * Math.cos((provider.lat * Math.PI) / 180);
        const dlat = (lat - provider.lat) * 111000;
        const dist = Math.sqrt(dlon * dlon + dlat * dlat);
        const radius = intent.radius_m || 1500;
        if (dist < radius) {
          setRequests((r) => [intent, ...r]);
        }
      }
      if (e.type === "intent.removed") {
        setRequests((r) => r.filter((x) => x.intent_id !== e.payload.intent_id));
      }
    }
    window.demoOn && window.demoOn(onMsg);
    return () => window.demoOff && window.demoOff(onMsg);
  }, [provider]);

  const handleBid = async (intent, price) => {
    const bid = {
      provider_id: provider.provider_id,
      price_cents: Math.round(price * 100),
      eta_minutes: 12,
      notes: "Can do in 20min",
    };
    try {
      const res = await submitBid(intent.intent_id, bid);
      if (res.ok) alert("Bid submitted");
    } catch (err) {
      alert(err.message || "Failed to submit bid");
    }
  };

  if (!provider) {
    return (
      <div className="small">Select a provider in demo mode to see the dashboard.</div>
    );
  }

  return (
    <div>
      <div className="header">
        <div className="logo">P</div>
        <div>
          <h3 className="h2">Provider Dashboard</h3>
          <div className="small">Provider: {provider.name}</div>
        </div>
      </div>
      <div className="small">Incoming requests</div>
      {requests.map((req) => (
        <div key={req.intent_id} className="card">
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <div>
              <strong>{req.raw_text || req.text}</strong>
              <div className="small">expires: {req.expires_at || "—"}</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <span className="badge">{Math.round(Math.random() * 100)}m</span>
            </div>
          </div>
          <div style={{ marginTop: 8 }}>
            <button className="btn" onClick={() => handleBid(req, 25)}>
              Offer CHF 25
            </button>
            <button
              style={{ marginLeft: 8 }}
              className="btn"
              onClick={() => handleBid(req, 20)}
            >
              Offer CHF 20
            </button>
          </div>
        </div>
      ))}
      {requests.length === 0 && (
        <div className="small">No nearby requests yet.</div>
      )}
    </div>
  );
}
