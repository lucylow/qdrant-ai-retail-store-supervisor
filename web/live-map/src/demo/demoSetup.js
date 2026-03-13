import { useEffect } from "react";

export function useDemoSetup({ setProviders, setIntents, setProviderProfile }) {
  useEffect(function () {
    var demoProviders = [
      { provider_id: "p_001", name: "Salon A", lat: 47.3776, lon: 8.5411, categories: ["haircut", "beard"] },
      { provider_id: "p_002", name: "Quick Trim", lat: 47.3748, lon: 8.5452, categories: ["haircut"] },
      { provider_id: "p_003", name: "Nails & Co", lat: 47.3792, lon: 8.5384, categories: ["manicure"] },
    ];
    setProviders(demoProviders);
    setProviderProfile(demoProviders[0]);
    window.demoEmit = function (event) {
      (window._demoListeners || []).forEach(function (fn) { fn(event); });
    };
    window.demoOn = function (fn) {
      window._demoListeners = window._demoListeners || [];
      window._demoListeners.push(fn);
    };
    window.demoOff = function (fn) {
      window._demoListeners = (window._demoListeners || []).filter(function (x) { return x !== fn; });
    };
    var saved = JSON.parse(localStorage.getItem("demo_intents") || "[]");
    saved.forEach(function (s) { setIntents(function (curr) { return [s].concat(curr); }); });
  }, [setProviders, setIntents, setProviderProfile]);
}
