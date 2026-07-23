const CACHE = 'mahir-pwa-v1';
const ASSETS = ['/app', '/pwa/manifest.json'];

self.addEventListener('install', e => {
    e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS).catch(() => { })));
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(caches.keys().then(keys =>
        Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ));
    self.clients.claim();
});

self.addEventListener('fetch', e => {
    const url = new URL(e.request.url);
    // Network-first for API calls
    if (url.pathname.startsWith('/api/')) {
        e.respondWith(fetch(e.request).catch(() => new Response(JSON.stringify({ response: 'You are offline. Please reconnect to chat with Mahir.' }), { headers: { 'Content-Type': 'application/json' } })));
        return;
    }
    // Cache-first for static assets
    e.respondWith(caches.match(e.request).then(cached => cached || fetch(e.request)));
});
