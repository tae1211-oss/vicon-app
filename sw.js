const CACHE_NAME = 'vicon-v38';

// ??猿띾뜲湲?HTML/?꾩씠肄?留?罹먯떆 ??Firebase ?곗씠?곕뒗 ??긽 ?ㅽ듃?뚰겕
const PRECACHE = [
  '/',
  '/index.html',
  '/icons/icon.svg',
  '/manifest.json'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(PRECACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Firebase / ?몃? API ?붿껌? ??긽 ?ㅽ듃?뚰겕
  if (
    url.hostname.includes('firestore.googleapis.com') ||
    url.hostname.includes('firebase') ||
    url.hostname.includes('googleapis.com') ||
    url.hostname.includes('gstatic.com') ||
    url.hostname.includes('cdnjs') ||
    url.hostname.includes('unpkg') ||
    url.hostname.includes('jsdelivr')
  ) {
    return; // 釉뚮씪?곗? 湲곕낯 ?숈옉 (?ㅽ듃?뚰겕)
  }

  // ??HTML? ?ㅽ듃?뚰겕 ?곗꽑 ???ㅽ뙣 ??罹먯떆
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match('/index.html'))
    );
    return;
  }

  // ?섎㉧吏 ?뺤쟻 ?뚯씪? 罹먯떆 ?곗꽑 ???놁쑝硫??ㅽ듃?뚰겕
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});


