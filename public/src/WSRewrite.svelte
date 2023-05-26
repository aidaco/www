<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import WSRewrite from "./lib/WSRewrite";
  let url = "/api/live";
  let activated = false;
  let content = "";

  let rewrite = new WSRewrite("/api/live", {
    oncommand: (command, data) => {
      switch (command) {
        case "CONNECT":
          break;
        case "ACTIVATE":
          activated = true;
          break;
        case "UPDATE":
          content = data;
          break;
        case "DEACTIVATE":
          activated = false;
          break;
      }
    },
    onclose: () => {
      activated = false;
    },
    onerror: (event) => {
      console.log(event);
    },
  });

  onMount(async () => {
    rewrite.connect();
  });

  onDestroy(() => {
    rewrite.disconnect();
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
