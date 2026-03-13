import Sockette from "sockette";

export function createSocket(url, onMessage, opts) {
  opts = opts || {};
  if (!url) return { close: function () {} };
  var s = new Sockette(url, Object.assign({
    timeout: 5000,
    maxAttempts: 10,
    onmessage: function (e) {
      try {
        var data = JSON.parse(e.data);
        if (onMessage) onMessage(data);
      } catch (err) {
        console.warn("ws parse err", err);
      }
    },
    onopen: function () { console.log("ws open"); },
    onclose: function () { console.log("ws close"); },
    onerror: function (e) { console.log("ws error", e); }
  }, opts));
  return s;
}
