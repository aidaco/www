<script>
	import { onMount, onDestroy } from 'svelte'
	const url = "wss://aidaco.dev/madness/live"
	let activated = false
	let content = ''
    var match_cmd = function(s) {
        var match = s.match('^([A-Za-z]*)( (.*))?')
        return [match[1], match[3]]
    }
	onMount(async () => {
		var ws = new WebSocket(url)
		ws.onerror = (event) => {
			console.log(event.data)
		}
		ws.onmessage = (event) => {
            var [cmd, value] = match_cmd(event.data)
            switch (cmd) {
                case 'CONNECT':
                    console.log('CONNECT', value)
                    break
                case 'ACTIVATE':
                    console.log('ACTIVATE')
                    activated = true
                    break
                case 'CLEAR':
                    console.log('CLEAR')
                    content = ''
                    break
                case 'UPDATE':
                    console.log('UPDATE ' + value)
                    content = value
                    break
                case 'APPEND':
                    console.log('APPEND ' + value)
                    content = content + value
                    break
                case 'DEACTIVATE':
                    console.log('DEACTIVATE')
                    activated = false
                    content = ''
                    break
            }
		}

		ws.onclose = (event) => {
			activated = false
			console.log('DISCONNECT')
		}
	})

	onDestroy(() => {
		ws.close()
		activated = false
	})
</script>

<div class='container'>
	{#if !activated}
		<slot></slot>
	{:else}
		<div class='madness'>{@html content}</div>
	{/if}
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

	.madness {
		overflow-wrap: break-word;
		overflow: hidden;
	}
</style>
