const makeUrlFromPath = (path: string) => {
  var protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
  var host = window.location.hostname;
  var defaultPort = window.location.protocol === "https:" ? "442" : "80";
  var port =
    window.location.port === defaultPort ? "" : ":" + window.location.port;
  return protocol + host + port + path;
};

const parseCommand = (source: string) => {
  let match = source.match("^([A-Za-z]*)( (.*))?");
  return [match[1], match[3]];
};

interface RewriteHandler {
  onerror: (event: Event) => void;
  onclose: () => void;
  oncommand: (type: string, value: string) => void;
}

export default class WSRewrite {
  url: string;
  handler: RewriteHandler;
  ws: WebSocket;
  constructor(path: string, handler: RewriteHandler) {
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
