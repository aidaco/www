<script lang="ts">
  import BorderCard from "./BorderCard.svelte";
  import Contact from "./Contact.svelte";
  import HireMe from "./HireMe.svelte";
  import WSRewrite from "./WSRewrite.svelte";

  let displayState: string = "home";
  let setDisplayState = (value: string) => (displayState = value);
</script>

<BorderCard>
  <WSRewrite>
    <div class="container">
      <ul class="nav">
        <li>
          <label>
            <input
              type="radio"
              bind:group={displayState}
              name="displayState"
              value={"home"}
              checked
            />
            <span class="nav-link">Home</span>
          </label>
        </li>
        <li>
          <label>
            <input
              type="radio"
              bind:group={displayState}
              name="displayState"
              value={"contact"}
            />
            <span class="nav-link">Contact</span>
          </label>
        </li>
        <li>
          <label>
            <input
              type="radio"
              bind:group={displayState}
              name="displayState"
              value={"hiring"}
            />
            <span class="nav-link">Hire Me</span>
          </label>
        </li>
      </ul>
      <div class="detail-view">
        {#if displayState === "home"}
          <div class="center-title">
            <h1>Aidan Courtney</h1>
            <h2>Software Developer</h2>
          </div>
        {:else if displayState === "contact"}
          <Contact />
        {:else if displayState === "hiring"}
          <HireMe />
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
  }

  .nav {
    display: flex;
    flex-direction: row;
    width: 95%;
    margin: 0;
    padding: 0.25rem 0 0 0;
    border-bottom: 0.1rem solid white;
    justify-content: space-evenly;
  }

  .nav > li > label > input {
    display: none;
  }

  .nav > li:hover {
    text-decoration: underline;
    font-style: italic;
  }

  :checked + span {
    text-decoration: overline;
  }

  .detail-view {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 95%;
    height: 95%;
    overflow: hidden;
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
