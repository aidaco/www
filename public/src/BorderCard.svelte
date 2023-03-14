<main>
  <div class='card' id='rewrite'>
    <div class='responsive-orientation'>
      <slot/>
    </div>
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
    min-height: 30vh;
    padding: 5vw;
    border: var(--border) solid 0.1em;
    display: flex;
    justify-content: space-evenly;
    align-items: center;
  }

  .responsive-orientation {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  @media screen and (max-width: 700px) {
    .responsive-orientation {
      flex-direction: column;
    }
  }
</style>
