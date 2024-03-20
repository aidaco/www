import { LiveClient } from "./liveclient.js";

var state = new Map();
var parent = document.querySelector("main > ul");

async function logout() {
  var response = await fetch('/auth/logout', {method: 'POST'})
  if (response.ok) {
    location.href = '/index.html'
  }
}

async function refreshAuth() {
    var data = [];
    for (var [k, v] of Object.entries({
      grant_type: "refresh_token",
      response_type: "cookie"
    })) {
      data.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
    }
    var resp = await fetch("/auth/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
      },
      body: data.join("&"),
    });
    if (!resp.ok) {
      throw new Error('Failed to authenticate')
    }
}

async function apiFetch(...args) {
  let response = await fetch(...args)
  if (!response.ok && response.status == 401) {
      await refreshAuth()
      response = await fetch(...args)
  }
  return response
}

async function refresh() {
  const response = await apiFetch("/api/state");
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

const makeUrlFromPath = (path) => {
  var protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
  var host = window.location.hostname;
  var defaultPort = window.location.protocol === "https:" ? "442" : "80";
  var port =
    window.location.port === defaultPort ? "" : ":" + window.location.port;
  return protocol + host + port + path;
};

const parseCommand = (source) => {
  let match = source.match("^([A-Za-z]*)( (.*))?");
  return [match[1], match[3]];
};

class WSRewrite {
  url;
  handler;
  ws;

  constructor(path, handler) {
    this.url = makeUrlFromPath(path);
    this.handler = handler;
  }

  connect() {
    this.ws = new WebSocket(this.url);
    let { oncommand, onclose, onerror } = this.handler;
    this.ws.onerror = onerror;
    this.ws.onclose = onclose;
    this.ws.onmessage = (event) => {
      let [command, data] = parseCommand(event.data);
      oncommand(command, data);
    };
  }

  disconnect() {
    this.ws.close();
  }
}

let livecontrol_auth_retry = true
let livecontrol

async function connect_livecontrol() {
  livecontrol = new WSRewrite("/controller", {
    oncommand: (command, data) => {
      console.log(command, data)
    },
    onclose: () => {
      console.log('close')
    },
    onerror: (event) => {
      console.log(event);
      if (livecontrol_auth_retry) {
        livecontrol_auth_retry = false
        (async () => {
          await refreshAuth();
          await connect_livecontrol();
        })();
      }
    },
  });
  livecontrol.connect();
}

document.querySelector('button.logout').addEventListener('click', logout)
addEventListener('load', connect_livecontrol)
addEventListener('beforeunload', event=>livecontrol.disconnect())
