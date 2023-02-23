<script lang="ts">
  import BorderCard from "/lib/BorderCard.svelte";

  let username;
  let password;

  async function do_login(event) {
    console.log(`POSTING ${username} ${password}`);
    var data = [];
    for (var [k, v] of Object.entries({
      username: username,
      password: password,
      grant_type: "password",
    })) {
      data.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
    }

    var resp = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
      },
      body: data.join("&"),
    });
    var respData = await resp.json();
    console.log(`Success ${JSON.stringify(respData)}`);
    document.cookie = `Authorization=${respData.access_token};secure;max-age=86400;`;
    location.href = '/madness'
  }
</script>

<main>
  <BorderCard>
    <div>
      <input
        type="text"
        name="username"
        placeholder="Username"
        bind:value={username}
      /><br />
      <input
        type="password"
        name="password"
        placeholder="Password"
        bind:value={password}
      /><br />
      <button on:click={do_login}>Submit</button>
    </div>
  </BorderCard>
</main>

<style>
  main {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  button {
	appearance: none;
	background-color: transparent;
	color: white;
	border: 2px solid gray;
	margin: 0.5rem;
	padding: 0.5rem;
	box-sizing: border-box;
	width: 100%;
  }

  input {
	appearance: none;
	background-color: transparent;
	border: 2px solid gray;
	color: white;
	padding: 0.5rem;
	margin: 0.5rem;
	width: 100%;
	box-sizing: border-box;
  }

  input::placeholder {
	color: lightgray;
	opacity: 1;
  }
</style>
