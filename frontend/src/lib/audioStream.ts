// audioStream.ts
export function createAudioStream(socket: any) {
  navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm'
    });

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0 && socket.connected) {
        const reader = new FileReader();
        reader.onload = () => {
          const base64 = (reader.result as string).split(',')[1];
          socket.emit("audio_chunk", base64);
        };
        reader.readAsDataURL(e.data);
      }
    };

    mediaRecorder.start(250); // Enviar cada 250ms

    socket.on("disconnect", () => {
      mediaRecorder.stop();
    });
  });
}
