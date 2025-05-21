export async function createAudioStream(socket: WebSocket) {
  const audioContext = new AudioContext();
  await audioContext.audioWorklet.addModule('/recorder.worklet.js');

  const recorderNode = new AudioWorkletNode(audioContext, 'recorder.worklet');
  recorderNode.port.onmessage = (event) => {
    const float32Array = event.data as Float32Array;
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      int16Array[i] = float32Array[i] * 32767;
    }
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(int16Array);
    }
  };

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const source = audioContext.createMediaStreamSource(stream);
  source.connect(recorderNode);
  recorderNode.connect(audioContext.destination);
  recorderNode.port.start();
  socket.addEventListener('close', () => {
    recorderNode.port.close();
    source.disconnect();
    audioContext.close();
  });
}