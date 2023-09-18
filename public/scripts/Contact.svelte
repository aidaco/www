<div class="container">
  <ul>
    <li>
      <a class="link" href="sms:+16317048992">631-704-8994</a>
      <br />
      <em>phone</em>
    </li>
    <li>
      <a class="link" href="mailto:aidanfc97@gmail.com">aidanfc97@gmail.com</a>
      <br />
      <em>email</em>
    </li>
    <li>
      <a class="link" href="https://www.linkedin.com/in/aidan-courtney"
        >aidan-courtney</a
      >
      <br />
      <em>linkedin</em>
    </li>
    <li>
      <a class="link" href="https://www.github.com/aidaco">aidaco</a>
      <br />
      <em>github</em>
    </li>
  </ul>
</div>

<style>
  .container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    font-size: 16px;
  }

  ul {
    margin: 0;
    padding: 0;
  }

  em {
    color: var(--content-highlight-alt);
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
</style>
