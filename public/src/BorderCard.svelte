<main>
  <div class='card' id='rewrite'>
    <slot/>
  </div>
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

  .card {
    background: var(--background-highlight);
    min-width: 40vw;
    min-height: 40vh;
    max-width: 80vw;
    max-height: 80vh;
    border: var(--border) solid 0.1em;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0;
    padding: 2rem;
    gap: 1rem;
  }
</style>
