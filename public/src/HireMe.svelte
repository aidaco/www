<script>
  const resumeUrl = new URL(
    "/assets/Aidan Courtney - Resume.pdf",
    import.meta.url
  ).href;
</script>

<div class="container">
  <span>
    Are you looking to hire an experienced software developer? Look no further!
    After out-growing my current position, I'm seeking a mid-level role with an
    emphasis on professional development. Python has been my language of choice
    for the last few years, but I enjoy learning new technologies and do so
    quickly. Take a look at <a href={resumeUrl}>my resume</a> and feel free to contact
    me for any reason.
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
