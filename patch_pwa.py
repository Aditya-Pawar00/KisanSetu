import os

for api_path in ['src/api.py', 'backend/src/api.py']:
    if os.path.exists(api_path):
        with open(api_path, 'r', encoding='utf-8') as f:
            code = f.read()
        if '/manifest.json' not in code:
            code += '''

@app.get("/manifest.json")
def get_manifest_json():
    from fastapi.responses import JSONResponse
    return {
        "name": "KisanSetu - Maharashtra APMC",
        "short_name": "KisanSetu",
        "start_url": "/",
        "id": "/",
        "display": "standalone",
        "background_color": "#f8fafc",
        "theme_color": "#15803d",
        "description": "Maharashtra 76 APMC Mandi Live Rates and Farmer Auction Slips",
        "icons": [
            {"src": "https://cdn-icons-png.flaticon.com/512/2990/2990479.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "https://cdn-icons-png.flaticon.com/512/2990/2990479.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
        ]
    }

@app.get("/sw.js")
def get_service_worker_file():
    from fastapi.responses import Response
    sw = "self.addEventListener('install', e => self.skipWaiting()); self.addEventListener('activate', e => clients.claim()); self.addEventListener('fetch', e => e.respondWith(fetch(e.request).catch(() => new Response('Offline'))));"
    return Response(content=sw, media_type="application/javascript")
'''
            with open(api_path, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f'Updated {api_path}')

for fe_path in ['src/frontend.html', 'backend/src/frontend.html']:
    if os.path.exists(fe_path):
        with open(fe_path, 'r', encoding='utf-8') as f:
            html = f.read()
        if '<link rel="manifest"' not in html:
            tags = '''  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#15803d">
  <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}));
    }
  </script>
</head>'''
            html = html.replace('</head>', tags)
            with open(fe_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f'Updated {fe_path}')

print("Done! Files updated.")
