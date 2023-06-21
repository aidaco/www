<script>
  const resumeUrl = new URL(
    "/assets/Aidan Courtney - Resume.pdf",
    import.meta.url
  ).href;
</script>

<div class="container">
  <span>
    Are looking for a driven and passionate software developer to join your
    team? Look no further! I am actively searching for an entry-to-mid level
    position at an organization that emphasizes ongoing professional
    development. Python has been my language of choice for the past few years,
    but I pride myself on quickly adapting to new technologies. I encourage you
    to review my <a href={resumeUrl}>my resume</a> and contact me at your convenience.
  </span>
</div>

<style>
  .container {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
  }

  span {
    margin: 0;
    padding: 0;
    font-size: 16px;
    text-align: center;
  }

  a {
    color: var(--content-accent);
    text-decoration: var(--content-accent) underline;
  }
</style>
