<main class="center-content">
  <div class="center-content box shifting-border">
    <slot />
  </div>
</main>

<style>
  main {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    background-image: radial-gradient(
      var(--background-accent),
      var(--background)
    );
    color: var(--content);
    font-family: monospace;
    font-size: 16px;
  }

  .center-content {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .box {
    width: 75%;
    height: 50%;
    margin: 0;
    padding: 0.75rem;
    gap: 1rem;
  }

  .shifting-border {
    background: var(--background-highlight);
    border-style: solid;
    border-width: 0;
    border-bottom-width: 1rem;
    --angle: 0deg;
    border-image: linear-gradient(
        var(--angle),
        hsl(var(--hue), 50%, 50%),
        hsl(var(--hue), 50%, 15%)
      )
      1;
    animation: 3s rotate linear infinite, 10s shift linear infinite;
  }

  @property --angle {
    syntax: "<angle>";
    initial-value: 0deg;
    inherits: false;
  }

  @property --hue {
    syntax: "<angle>";
    initial-value: 0deg;
    inherits: false;
  }

  @keyframes shift {
    to {
      --hue: 360deg;
    }
  }

  @keyframes rotate {
    to {
      --angle: 360deg;
    }
  }
</style>
