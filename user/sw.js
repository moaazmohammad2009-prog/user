/**
 * Lucky48 Progressive Web App - Service Worker
 * Strategy: Cache-First with Stale-While-Revalidate Fallback
 * Version: 1.0.2
 */

const CACHE_VERSION = 'v1.0.2';
const STATIC_CACHE_NAME = `lucky48-static-${CACHE_VERSION}`;
const DYNAMIC_CACHE_NAME = `lucky48-dynamic-${CACHE_VERSION}`;

const CORE_ASSETS = [
  './',
  './index.html',
  './host.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

// 1. Install Event: Pre-cache core application shell assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Pre-caching App Shell');
        return cache.addAll(CORE_ASSETS);
      })
      .catch((error) => console.error('[Service Worker] Pre-cache failed:', error))
  );
  self.skipWaiting();
});

// 2. Activate Event: Clean up outdated cache versions
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== STATIC_CACHE_NAME && key !== DYNAMIC_CACHE_NAME) {
            console.log('[Service Worker] Removing old cache:', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// 3. Fetch Event: Handle requests with Network-First/Cache-First hybrid strategy
self.addEventListener('fetch', (event) => {
  // Ignore non-GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Return cached version immediately & revalidate in background
        fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              caches.open(STATIC_CACHE_NAME).then((cache) => {
                cache.put(event.request, networkResponse.clone());
              });
            }
          })
          .catch(() => /* Suppress network error in offline mode */ {});

        return cachedResponse;
      }

      // If not in cache, fetch from network and store in dynamic cache
      return fetch(event.request)
        .then((networkResponse) => {
          if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
            return networkResponse;
          }

          const responseToCache = networkResponse.clone();
          caches.open(DYNAMIC_CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });

          return networkResponse;
        })
        .catch(() => {
          // Offline fallback for navigation requests
          if (event.request.headers.get('accept')?.includes('text/html')) {
            return caches.match('./index.html');
          }
        });
    })
  );
});