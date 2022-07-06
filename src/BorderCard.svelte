<div class='container'>
	<slot></slot>
</div>

<style>
	.container {
		width: 100vw;
		height: calc(52vh - 1rem);
		margin: 12vh 0;
		padding: 12vh 0;
		display: flex;
		border: white solid;
		border-width: 0.5rem 0;
		justify-content: space-evenly;
		align-items: center;
	}
</style>
