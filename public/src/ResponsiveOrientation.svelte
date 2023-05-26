<div class="responsive-orientation">
  <slot />
</div>

<style>
  .responsive-orientation {
    width: 100%;
    height: 100%;
    max-width: 80vw;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin: 2rem;
    padding: 0;
    gap: 1rem;
  }

  @media screen and (max-width: 700px) {
    .responsive-orientation {
      flex-direction: column;
    }
  }
</style>
