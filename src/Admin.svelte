<script lang="ts">
  import BorderCard from "./BorderCard.svelte";
  import LiveControl from "./LiveControl.svelte";
  import { onMount } from "svelte";

  var state = {};
  async function refresh() {
    const response = await fetch("/api/state");
    state = await response.json();
  }

  async function auto_refresh() {
    refresh();
    setTimeout(auto_refresh, 5000);
  }

  onMount(async () => {
    auto_refresh();
  });
</script>

<main>
  <BorderCard>
    {#if Object.keys(state).length > 0}
      <ul>
        {#each Object.entries(state) as [uid, [active, content]]}
          <li>
            <LiveControl {uid} {active} {content} />
          </li>
        {/each}
      </ul>
    {:else}
      <div>No Connections.</div>
    {/if}
  </BorderCard>
</main>

<style>
  main {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
  }

  ul {
    list-style-type: none;
  }
</style>
