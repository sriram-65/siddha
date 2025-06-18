self.addEventListener("install" , (e)=>{
    e.waitUntil(
        caches.open("offile-cache").then((cache)=>{
            return cache.addAll(["/offile.html"])
        })
    )
})


self.addEventListener("fetch" , (e)=>{
    e.respondWith(
        fetch(e.request).catch(()=>{
            return caches.match("offile-cache")
        })
    )
})
