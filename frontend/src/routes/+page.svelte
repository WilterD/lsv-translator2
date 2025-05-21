<script lang="ts">
  import { onMount } from 'svelte';
  import { createAudioStream } from '$lib/audioStream';
  import { loadAvatar, enqueueAnimation } from '$lib/avatarControl';

  let transcript: string[] = [];
  let canvas: HTMLCanvasElement;
  let resumen = "";

  let socket: WebSocket;

  onMount(() => {
    loadAvatar(canvas, '/avatar.glb');
    socket = new WebSocket('ws://localhost:5000/stream');

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      transcript.push(data.glosa);
      enqueueAnimation(data.animacion);
    };
  });

  function start() {
    createAudioStream(socket);
  }

  async function obtenerResumen() {
    const res = await fetch('/resumen');
    const json = await res.json();
    resumen = json.resumen;
  }
</script>

<h1>Traductor Voz → Glosa → Animación</h1>
<button on:click={start}>🎙️ Iniciar reconocimiento</button>
<button on:click={obtenerResumen}>🧠 Resumen</button>
<p><strong>Glosas reconocidas:</strong> {transcript.join(' ')}</p>
<p><strong>Resumen:</strong> {resumen}</p>
<canvas bind:this={canvas}></canvas>

<style>
  canvas {
    border: 1px solid #ccc;
    margin-top: 1rem;
    width: 100%;
    max-width: 600px;
    height: auto;
  }
</style>
