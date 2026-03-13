import React, { useState } from "react";
import { createIntent } from "../api";

export default function IntentComposer({ userLocation, onCreated }) {
  const [text, setText] = useState("");
  const [radius, setRadius] = useState(1200);
  const [ttl, setTtl] = useState(15);
  const [status, setStatus] = useState(null);

  const handleSubmit = async () => {
    if (!text.trim()) {
      alert("Enter request text");
      return;
    }
    setStatus("sending");
    try {
      const payload = {
        user_id: "demo_user",
        raw_text: text.trim(),
        text: text.trim(),
        lat: userLocation.lat,
        lon: userLocation.lon,
        radius_m: Number(radius),
        ttl_minutes: Number(ttl),
        max_walk_minutes: 20,
        consent: {
          scope: ["match", "push"],
          granted_at: new Date().toISOString(),
          exact_share: false,
        },
      };
      const res = await createIntent(payload);
      const intentId = res.intent_id;
      setStatus("sent");
      onCreated && onCreated(intentId);
      setText("");
    } catch (err) {
      setStatus("error");
      alert(err.message || "Failed to create intent");
    }
  };

  return (
    <div>
      <div className="header">
        <div className="logo">LM</div>
        <div>
          <h3 className="h2">Broadcast Intent</h3>
          <div className="small">Let nearby providers compete to serve you</div>
        </div>
      </div>
      <textarea
        className="input"
        rows={3}
        placeholder="e.g. Quick haircut near Zurich HB at 16:00, under 40 CHF"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <label className="small" style={{ marginBottom: 0 }}>
          Radius (m): <input className="input" type="number" style={{ width: 80 }} value={radius} onChange={(e) => setRadius(e.target.value)} />
        </label>
        <label className="small" style={{ marginBottom: 0 }}>
          TTL (min): <input className="input" type="number" style={{ width: 60 }} value={ttl} onChange={(e) => setTtl(e.target.value)} />
        </label>
      </div>
      <button className="btn" onClick={handleSubmit} disabled={status === "sending"}>
        Broadcast
      </button>
      {status && (
        <div style={{ marginTop: 8 }} className="small">
          Status: {status}
        </div>
      )}
    </div>
  );
}
