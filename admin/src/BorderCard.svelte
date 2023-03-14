<div class="container">
  <slot />
</div>

<style>
  .container {
    min-width: 40vw;
    min-height: 30vh;
    padding: 5vw;
    border: gray solid;
    border-width: 0.25rem;
    display: flex;
    justify-content: space-evenly;
    align-items: center;
  }
</style>
