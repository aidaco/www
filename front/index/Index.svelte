<script lang="ts">
  import BorderCard from "/lib/BorderCard.svelte";
  import WSRewrite from "/lib/WSRewrite.svelte";
</script>

<main>
  <BorderCard>
    <WSRewrite>
      <div class="rot-cont">
        <div id="name-title">
          <h2>Aidan Courtney</h2>
          <em>Software Developer</em>
        </div>
        <ul>
          <li>ph<b>|</b><a href="sms:+16317048994">631-704-8994</a></li>
          <li>
            em<b>|</b><a href="mailto:aidanfc97@gmail.com"
              >aidanfc97@gmail.com</a
            >
          </li>
          <li>gh<b>|</b><a href="https://github.com/aidaco">aidaco</a></li>
          <li>
            li<b>|</b><a href="https://www.linkedin.com/in/aidan-courtney"
              >aidan-courtney</a
            >
          </li>
        </ul>
      </div>
    </WSRewrite>
  </BorderCard>
</main>

<style>
  a {
    color: rgb(105, 155, 255);
    text-decoration: none;
  }

  a:hover {
    text-transform: underline;
  }

  a:hover::after {
    content: " 🔗";
  }

  a:visited {
    color: rgb(166, 104, 227);
  }

  main {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .rot-cont {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  #name-title {
    text-align: center;
  }

  h2,
  ul {
    margin: 10px;
  }

  ul {
    list-style: none;
    font-size: 14px;
    display: flex;
    flex-direction: column;
  }

  li > b {
    font-size: 18px;
  }

  @media screen and (max-width: 700px) {
    .rot-cont {
      flex-direction: column;
    }
  }
</style>
