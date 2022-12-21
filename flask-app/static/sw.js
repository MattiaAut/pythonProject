let cacheName = 'FrontlineCode';
let filesToCache = [
    'index.html',
    'css/style.css',
    'js/main.js'
];
/* Start the service worker and cache all of the app's content */
self.addEventListener("install", (event) => {
    console.log("Service Worker : Installed!")

    event.waitUntil(

        (async() => {
            try {
                cache_obj = await caches.open(cache)
                cache_obj.addAll(caching_files)
            }
            catch{
                console.log("error occured while caching...")
            }
        })()
    )
} )

/* Serve cached content when offline */
self.addEventListener('fetch', function(e) {
    e.respondWith(
        caches.match(e.request).then(function(response) {
            return response || fetch(e.request);
        })
    );
});

