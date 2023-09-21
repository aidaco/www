import { LiveClient } from "./liveclient.js";

var state = new Map();
var parent = document.querySelector("main > ul");

async function refresh() {
  const response = await fetch("/api/state");
  let update = new Map(Object.entries(await response.json()));
  [...state.keys()]
    .filter((uid) => !update.has(uid))
    .map((uid) => {
      state.get(uid).disconnect();
      state.delete(uid);
    });

  if (update.size === 0) return;

  update.forEach(([active, content], uid, map) => {
    if (state.has(uid)) {
      state.get(uid).set(active, content);
    } else {
      let client = new LiveClient(parent, uid, active, content);
      state.set(uid, client);
    }
  });
}

async function auto_refresh() {
  await refresh();
  setTimeout(auto_refresh, 5000);
}

auto_refresh();
