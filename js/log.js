function log(message) {
  const el = document.getElementById("log");
  const line = document.createElement("div");
  const time = new Date().toLocaleTimeString();
  line.textContent = `[${time}] ${message}`;
  el.appendChild(line);
  el.scrollTop = el.scrollHeight;
  console.log(message);
}

function logError(prefix, err) {
  log(`${prefix}: ${err && err.message ? err.message : err}`);
  console.error(prefix, err);
}
