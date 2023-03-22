<script>
  import BorderCard from "./BorderCard.svelte"
</script>

<BorderCard>
  <div class="container">
    <div class="center-title">
      <h1>Aidan Courtney</h1>
      <h2>Contact Info</h2>
    </div>
    <ul>
      <li><em>phone</em><b>::</b><a class="link" href="sms:+16317048992">631-704-8994</a></li>
      <li><em>email</em><b>::</b><a class="link" href="mailto:aidanfc97@gmail.com">aidanfc97@gmail.com</a></li>
      <li><em>linkedin</em><b>::</b><a class="link" href="https://www.linkedin.com/in/aidan-courtney">aidan-courtney</a></li>
    </ul>
    <a class="home" href="/">⌂</a>
  </div>
</BorderCard>

<style>
  .container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 1rem;
  }

  .center-title {
    text-align: center;
  }

  h1,
  h2,
  ul {
    margin: 0;
    padding: 0;
  }

  em {
    color: var(--content-highlight-alt);
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
  }

  a {
    color: var(--content-accent);
  }

  .link {
    text-decoration: var(--content-accent) underline;
  }

  .link:hover::after {
    content: " 🔗";
    position: absolute;
    start: 3px;
  }

  .home {
    text-decoration: none;
    font-size: 4rem;
  }
</style>
