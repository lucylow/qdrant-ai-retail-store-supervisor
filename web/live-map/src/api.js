/**
 * LiveMap API helpers.
 * Compatible with FastAPI app/livemap_api.py:
 *   POST /livemap/intent expects: user_id, text, lat, lon, radius_m, max_walk_minutes, ttl_minutes, exact_share
 *   Returns full IntentOut (intent_id, ...) or we accept { ok: true, intent_id } from demo.
 */
const API_BASE = process.env.REACT_APP_API_BASE || "";
const useDemo = !API_BASE;

export async function createIntent(payload) {
  if (useDemo) {
    const id = "i_" + Math.random().toString(36).slice(2, 9);
    const intent = {
      intent_id: id,
      raw_text: payload.raw_text || payload.text,
      text: payload.raw_text || payload.text,
      lat: payload.lat,
      lon: payload.lon,
      radius_m: payload.radius_m || 1500,
      ttl_minutes: payload.ttl_minutes || 15,
      expires_at: new Date(Date.now() + (payload.ttl_minutes || 15) * 60 * 1000).toISOString(),
      created_at: new Date().toISOString(),
    };
    const d = JSON.parse(localStorage.getItem("demo_intents") || "[]");
    d.push(intent);
    localStorage.setItem("demo_intents", JSON.stringify(d));
    window.demoEmit && window.demoEmit({ type: "intent.created", payload: intent });
    return { ok: true, intent_id: id, ...intent };
  }
  const body = {
    user_id: payload.user_id || "demo_user",
    text: payload.raw_text || payload.text,
    lat: payload.lat,
    lon: payload.lon,
    radius_m: Number(payload.radius_m ?? 1500),
    max_walk_minutes: Number(payload.max_walk_minutes ?? 20),
    ttl_minutes: Number(payload.ttl_minutes ?? 15),
    exact_share: payload.consent?.exact_share ?? false,
  };
  const res = await fetch(`${API_BASE}/livemap/intent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to create intent");
  return { ok: true, intent_id: data.intent_id, ...data };
}

export async function getCandidates(intentId) {
  if (useDemo) return { intent: null, candidates: [] };
  const res = await fetch(`${API_BASE}/livemap/intent/${intentId}/candidates`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to load candidates");
  return data;
}

export async function submitBid(intentId, bid) {
  if (useDemo) {
    const b = {
      bid_id: "b_" + Math.random().toString(36).slice(2, 8),
      intent_id: intentId,
      ...bid,
      created_at: new Date().toISOString(),
    };
    const bs = JSON.parse(localStorage.getItem("demo_bids") || "[]");
    bs.push(b);
    localStorage.setItem("demo_bids", JSON.stringify(bs));
    window.demoEmit && window.demoEmit({ type: "bid.submitted", payload: b });
    return { ok: true, bid: b };
  }
  const res = await fetch(`${API_BASE}/livemap/intent/${intentId}/bid`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bid),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to submit bid");
  return data;
}

export async function chooseBid(intentId, bidId) {
  if (useDemo) {
    window.demoEmit &&
      window.demoEmit({
        type: "booking.created",
        payload: {
          booking_id: "bk_" + Math.random().toString(36).slice(2, 8),
          intent_id: intentId,
          bid_id: bidId,
        },
      });
    return { ok: true };
  }
  const res = await fetch(`${API_BASE}/livemap/intent/${intentId}/choose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ bid_id: bidId }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to choose bid");
  return data;
}
