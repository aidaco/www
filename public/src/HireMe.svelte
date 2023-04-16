<script>
  import BorderCard from "./BorderCard.svelte"
  import resumeUrl from "/assets/Aidan Courtney - Resume.pdf"
</script>

<BorderCard>
  <div class="container">
    <h1>Experienced Python Developer for Hire</h1>
    <span>
    Hi! I'm Aidan, a software developer with 10+ years of self-study and independent experience seeking opportunities to work on broader & more collaborative projects. My focus has been primarily Python, but I'm always excited for the opportunity to work with anything unfamiliar to me. If you are looking for a self-motivated developer to join your team, take a look at <a href={resumeUrl}>my resume</a> and <a href="/contact/">contact me</a>!
    </span>
    <a class="home" href="/">⌂</a>
  </div>
</BorderCard>

<style>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
  }

  h1 {
    margin: 0;
    padding: 0;
    font-size: 24px;
  }

  span {
    margin: 0;
    padding: 0;
  }

  a {
    color: var(--content-accent);
    text-decoration: var(--content-accent) underline;
  }

  .home {
    text-decoration: none;
    font-size: 4rem;
  }
</style>
