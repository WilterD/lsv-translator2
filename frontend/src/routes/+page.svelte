<script lang="ts">
  import { onMount } from 'svelte';
  import { loadAvatar, enqueueAnimation } from '$lib/avatarControl';
  import { io } from 'socket.io-client';

  let transcript: string[] = [];
  let canvas: HTMLCanvasElement;
  let socket: any;

  onMount(() => {
    loadAvatar(canvas, '/avatar.glb');

    socket = io("http://localhost:5000");

    socket.on("connect", () => {
      console.log("✅ Conectado a backend vía Socket.IO");
    });

    socket.on("glosa", (data: { glosa: string; animacion?: string }) => {
      console.log("✋ Glosa detectada:", data.glosa);
      transcript = [...transcript, data.glosa];
      if (data.animacion) {
        enqueueAnimation(data.animacion);
      }
    });

    socket.on("estado", (data: { mensaje: string }) => {
      console.log("ℹ️", data.mensaje);
    });

    socket.on("error", (e: { error: string }) => {
      alert("❌ Error en el backend: " + e.error);
    });
  });

  function startRecognition() {
    socket.emit("iniciar_reconocimiento");
  }

  function playCasa() {
    console.log("▶️ Reproduciendo animación: Casa");
    enqueueAnimation("Casa");
  }
</script>

<h1>🧠 Traductor Voz → Glosa → Animación</h1>
<button on:click={startRecognition}>🎤 Iniciar reconocimiento</button>
<button on:click={playCasa}>🕹️ Reproducir "Casa"</button>
<p><strong>Glosas:</strong> {transcript.join(' ')}</p>
<canvas bind:this={canvas}></canvas>
