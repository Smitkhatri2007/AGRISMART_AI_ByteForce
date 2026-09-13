// ==========================================================================
// AgriSmart AI - Service Worker (PWA Offline Resilience)
// ==========================================================================

const CACHE_NAME = 'agrismart-cache-v1';
const STATIC_ASSETS = [
    './',
    './index.html',
    './manifest.json',
    './css/style.css',
    './css/variables.css',
    './css/layout.css',
    './css/components.css',
    './assets/icon.svg',
    './js/config.js',
    './js/i18n.js',
    './js/state.js',
    './js/tabs.js',
    './js/ui.js',
    './js/history.js',
    './js/camera.js',
    './js/api.js',
    './js/voice.js',
    './js/advisory.js',
    './js/agentic.js',
    './js/chat.js',
    './js/app.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Bypass caching for API endpoints and non-GET requests
    if (event.request.method !== 'GET' || url.pathname.startsWith('/api/') || url.hostname.includes('open-meteo.com')) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
                // Return cached asset, fetch update in background
                fetch(event.request).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, networkResponse));
                    }
                }).catch(() => {});
                return cachedResponse;
            }
            return fetch(event.request).then((networkResponse) => {
                if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                    return networkResponse;
                }
                const responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseToCache);
                });
                return networkResponse;
            });
        })
    );
});
