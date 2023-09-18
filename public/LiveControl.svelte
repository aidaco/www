<script>
  function dispatch(command, uid, content = "") {
    fetch("/api/dispatch", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        command: command,
        uid: uid,
        content: content,
      }),
    });
  }

  function activate() {
    dispatch("ACTIVATE", uid);
    active = true;
  }

  function update() {
    dispatch("UPDATE", uid, content);
  }

  function deactivate() {
    dispatch("DEACTIVATE", uid);
    active = false;
  }
  export let uid;
  export let active;
  export let content;
</script>

<div>
  {#if !active}
    <button class="connected" on:click={activate}>{uid}</button>
    <input type="text" bind:value={content} disabled />
  {:else}
    <button class="activated" on:click={deactivate}>{uid}</button>
    <input type="text" bind:value={content} on:input={update} />
  {/if}
</div>

<style>
  button {
    background-color: #454545;
    border-radius: 5px;
    color: white;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
  }

  input {
    background-color: #454545;
    border-radius: 5px;
    border: 2px solid white;
    color: white;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
  }

  .connected {
    border: 2px solid #f3172d;
  }
  .activated {
    border: 2px solid #66ff00;
  }
</style>
