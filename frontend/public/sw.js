/* Service worker BookMatch: оболочка приложения работает офлайн, каталог и теги - из кеша, если нет сети. */
const VERSION = 'v1'
const SHELL_CACHE = `bookmatch-shell-${VERSION}`
const DATA_CACHE = `bookmatch-data-${VERSION}`
const IMG_CACHE = `bookmatch-img-${VERSION}`
const SHELL = ['/', '/manifest.webmanifest', '/favicon.svg', '/icons/icon-192.png', '/icons/icon-512.png']

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(SHELL_CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()))
})

self.addEventListener('activate', (event) => {
  const keep = [SHELL_CACHE, DATA_CACHE, IMG_CACHE]
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => !keep.includes(k)).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  )
})

const isPublicApi = (url) => /\/(books|tags)(\/|$|\?)/.test(url.pathname) && !/card\.png$/.test(url.pathname)

async function networkFirst(request, cacheName, fallbackUrl) {
  const cache = await caches.open(cacheName)
  try {
    const response = await fetch(request)
    if (response.ok) cache.put(request, response.clone())
    return response
  } catch (err) {
    const cached = await cache.match(request) || (fallbackUrl && await caches.match(fallbackUrl))
    if (cached) return cached
    throw err
  }
}

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName)
  const cached = await cache.match(request)
  if (cached) return cached
  const response = await fetch(request)
  if (response.ok || response.type === 'opaque') cache.put(request, response.clone())
  return response
}

self.addEventListener('fetch', (event) => {
  const { request } = event
  if (request.method !== 'GET') return
  const url = new URL(request.url)

  // страницы SPA: сеть, при её отсутствии - закешированная оболочка
  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request, SHELL_CACHE, '/'))
    return
  }

  // обложки (в т.ч. с чужих доменов)
  if (request.destination === 'image') {
    event.respondWith(cacheFirst(request, IMG_CACHE).catch(() => Response.error()))
    return
  }

  // собственные статические файлы (хешированные сборкой)
  if (url.origin === self.location.origin && !url.pathname.startsWith('/api/')) {
    event.respondWith(cacheFirst(request, SHELL_CACHE))
    return
  }

  // публичные данные каталога (книги, теги) - сеть, потом кеш. Личные данные (/library, /quiz, /comments) не кешируются.
  if (isPublicApi(url)) {
    event.respondWith(networkFirst(request, DATA_CACHE))
  }
})
