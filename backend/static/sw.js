const CACHE = 'mahir-pwa-v2';
const ASSETS = ['/static/chat.html', '/static/manifest.json'];

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
    if (url.pathname.startsWith('/api/')) {
        e.respondWith(fetch(e.request).catch(() => new Response(JSON.stringify({ response: 'أنت غير متصل بالإنترنت. يرجى محاولة الاتصال من جديد.' }), { headers: { 'Content-Type': 'application/json' } })));
        return;
    }
    e.respondWith(caches.match(e.request).then(cached => cached || fetch(e.request)));
});
