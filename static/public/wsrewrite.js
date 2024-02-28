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

export class WSRewrite {
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
