<script lang="ts">
  import BorderCard from "./BorderCard.svelte"
  import WSRewrite from "./WSRewrite.svelte"
</script>

<BorderCard>
  <WSRewrite>
    <div class="center-title">
      <h1>Aidan Courtney</h1>
      <h2>Software Developer</h2>
    </div>
    <ul>
      <li><b>::</b><a href="/hireme/">Hire Me!</a></li>
      <li><b>::</b><a href="/contact/">Contact</a></li>
      <li><b>::</b><a href="https://github.com/aidaco">GitHub</a></li>
    </ul>
  </WSRewrite>
</BorderCard>

<style>
  h1,
  h2,
  ul {
    margin: 0;
    padding: 0;
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

  b {
    color: var(--content-division);
  }

  ul {
    list-style: none;
    display: flex;
    flex-direction: column;
  }

  li {
    margin: 0.3em 0 0.3em 0;
    font-size: 1.25rem;
  }

  a {
    color: var(--content-accent);
    text-decoration: var(--content-accent) underline;
  }

  a:hover::after {
    content: " 🔗";
    position: absolute;
    start: 3px;
  }
</style>
