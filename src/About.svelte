<script>
	import BorderCard from './BorderCard.svelte'
</script>

<BorderCard>
  <div class='rot-cont'>
    <div id='name-title'>
      <h2>Aidan Courtney</h2>
      <em>Software Developer</em>
    </div>
    <ul>
      <li>ph<b>|</b><a href="sms:+16317048994">631-704-8994</a></li>
      <li>em<b>|</b><a href="mailto:aidanfc97@gmail.com">aidanfc97@gmail.com</a></li>
      <li>gh<b>|</b><a href="https://github.com/aidaco">aidaco</a></li>
      <li>li<b>|</b><a href="https://www.linkedin.com/in/aidan-courtney">aidan-courtney</a></li>
    </ul>
  </div>
</BorderCard>

<style>

  .rot-cont {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  #name-title {
    text-align: center;
  }

  h2, ul {
    margin: 10px;
  }

	ul {
		list-style: none;
		font-size: 14px;
		display: flex;
		flex-direction: column;
	}

	li>b {
	  font-size: 18px;
	}

	@media screen and (max-width: 700px) {
		.rot-cont {
			flex-direction: column;
		}
	}
</style>
