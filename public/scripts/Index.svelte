<script lang="ts">
  import BorderCard from "./BorderCard.svelte";
  import Contact from "./Contact.svelte";
  import Hire from "./Hire.svelte";
  import WSRewrite from "./WSRewrite.svelte";
  import url from "./lib/url";
</script>

<BorderCard>
  <WSRewrite>
    <div class="container">
      <ul class="nav">
        <li>
          {#if $url.hash === "#home" || $url.hash === ""}
            <a href="#home" class="nav-link nav-current">Home</a>
          {:else}
            <a href="#home" class="nav-link">Home</a>
          {/if}
        </li>
        <li>
          {#if $url.hash === "#contact"}
            <a href="#contact" class="nav-link nav-current">Contact</a>
          {:else}
            <a href="#contact" class="nav-link">Contact</a>
          {/if}
        </li>
        <li>
          {#if $url.hash === "#hire"}
            <a href="#hire" class="nav-link nav-current">Hire</a>
          {:else}
            <a href="#hire" class="nav-link">Hire</a>
          {/if}
        </li>
      </ul>
      <div class="detail-view">
        {#if $url.hash === "#home" || $url.hash === ""}
          <div class="center-title">
            <h1>Aidan Courtney</h1>
            <h2>Software Developer</h2>
          </div>
        {:else if $url.hash === "#contact"}
          <Contact />
        {:else if $url.hash === "#hire"}
          <Hire />
        {/if}
      </div>
    </div>
  </WSRewrite>
</BorderCard>

<style>
  .container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow: hidden;
  }

  .nav {
    display: flex;
    flex-direction: row;
    width: 100%;
    height: 10%;
    margin: 0;
    padding: 0.25rem 0 0 0;
    border-bottom: 0.1rem solid white;
    justify-content: space-evenly;
  }

  .nav-link {
    color: var(--content);
    font-size: 1.5rem;
    text-decoration: underline;
  }

  .nav-link:hover {
    font-style: italic;
  }

  .nav-current {
    text-decoration: overline;
  }

  .detail-view {
    width: 80%;
    height: 90%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: auto;
  }

  .center-title {
    text-align: center;
  }

  h1 {
    font-size: 2em;
    color: var(--content);
  }

  h2 {
    font-size: 1.25em;
    color: var(--content-highlight);
  }

  ul {
    list-style: none;
    display: flex;
    flex-direction: column;
  }
</style>
