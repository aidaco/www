<script>
  import { onMount, onDestroy } from "svelte";
  const url = "/api/live";
  let activated = false;
  let content = "";

  function makeWebSocket(path) {
    var protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    var host = window.location.hostname;
    var defaultPort = window.location.protocol === "https:" ? "443" : "80";
    var port =
      window.location.port === defaultPort ? "" : ":" + window.location.port;
    return new WebSocket(protocol + host + port + path);
  }

  var match_cmd = function (s) {
    var match = s.match("^([A-Za-z]*)( (.*))?");
    return [match[1], match[3]];
  };
  onMount(async () => {
    var ws = makeWebSocket(url);
    ws.onerror = (event) => {
      console.log(event.data);
    };
    ws.onmessage = (event) => {
      var [cmd, value] = match_cmd(event.data);
      switch (cmd) {
        case "CONNECT":
          break;
        case "ACTIVATE":
          activated = true;
          break;
        case "UPDATE":
          content = value;
          break;
        case "DEACTIVATE":
          activated = false;
          break;
      }
    };

    ws.onclose = (event) => {
      activated = false;
    };
  });

  onDestroy(() => {
    ws.close();
    activated = false;
  });
</script>

{#if !activated}
  <slot />
{:else}
  <div class="madness">{@html content}</div>
{/if}

<style>
  .madness {
    overflow-wrap: break-word;
    overflow: hidden;
  }
</style>
