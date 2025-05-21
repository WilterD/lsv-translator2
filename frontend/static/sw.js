self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('voz-lsv-cache').then(cache => {
      return cache.addAll([
        '/',
        '/manifest.webmanifest',
        '/vosk.wasm',
        '/vosk-worker.js',
        '/model.tar.gz',
        '/avatar.glb',
        '/icon-192.png',
        '/icon-512.png'
      ]);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});