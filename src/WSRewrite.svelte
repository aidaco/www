<script>
	import { onMount, onDestroy } from 'svelte'
	const url = "ws://localhost:8000/api/live"
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
			    break
			case 'ACTIVATE':
			    activated = true
			    break
			case 'UPDATE':
			    content = value
			    break
			case 'DEACTIVATE':
			    activated = false
			    break
		    }
		}

		ws.onclose = (event) => {
			activated = false
		}
	})

	onDestroy(() => {
		ws.close()
		activated = false
	})
</script>

{#if !activated}
	<slot></slot>
{:else}
	<div class='madness'>{@html content}</div>
{/if}

<style>
	.madness {
		overflow-wrap: break-word;
		overflow: hidden;
	}
</style>
