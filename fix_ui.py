import os
import zlib
import struct

# 1. Pure Python PNG Generator (Zero External Libraries, No PIL needed)
def generate_png(size=192):
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            dx = x - size / 2
            dy = y - size / 2
            dist_sq = dx * dx + dy * dy
            r_out = (size * 0.46) ** 2
            r_in = (size * 0.41) ** 2

            if dist_sq <= r_in:
                if y > size * 0.58:
                    raw.extend([34, 197, 94, 255]) # green field
                elif dist_sq <= (size * 0.18) ** 2:
                    raw.extend([245, 158, 11, 255]) # gold sun
                else:
                    raw.extend([15, 23, 42, 255]) # dark slate
            elif dist_sq <= r_out:
                raw.extend([16, 185, 129, 255]) # emerald border
            else:
                raw.extend([0, 0, 0, 0]) # transparent

    comp = zlib.compressobj()
    compressed = comp.compress(raw) + comp.flush()

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')
    return png

png_data = generate_png(192)

for p in ['src', 'backend/src', '.']:
    if os.path.exists(p):
        with open(os.path.join(p, 'icon.png'), 'wb') as f:
            f.write(png_data)
print("Saved icon.png without PIL!")

# 2. Update api.py to serve /icon.png
for api_path in ['src/api.py', 'backend/src/api.py']:
    if os.path.exists(api_path):
        with open(api_path, 'r', encoding='utf-8') as f:
            api_c = f.read()
        
        api_c = api_c.replace("https://cdn-icons-png.flaticon.com/512/2990/2990479.png", "/icon.png")
        
        if '@app.get("/icon.png")' not in api_c:
            api_c += """

@app.get("/icon.png")
def serve_app_icon():
    from fastapi.responses import FileResponse, Response
    for p in ["icon.png", "src/icon.png", "backend/src/icon.png"]:
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    return Response(status_code=404)
"""
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(api_c)
        print(f"Updated {api_path} with /icon.png endpoint")

# 3. Update frontend.html: Zero-Overlap Ticker & App Logo
new_ticker_html = """  <!-- Live Marquee Ticker (Isolated, Zero-Overlap) -->
  <div class="relative z-50 w-full bg-gradient-to-r from-emerald-800 via-emerald-700 to-amber-600 text-xs font-bold shadow-sm flex items-center py-1 px-2 overflow-hidden border-b border-emerald-900/30">
    <!-- Opaque Fixed Left Badge (z-20 so text NEVER passes through) -->
    <div class="z-20 flex-shrink-0 px-2 sm:px-2.5 py-0.5 bg-slate-900 text-amber-300 text-[10px] sm:text-[11px] font-black rounded-lg mr-2 flex items-center gap-1.5 border border-amber-400/40 shadow">
      <span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span>
      <span id="ticker-badge" class="whitespace-nowrap">🔴 थेट बातम्या</span>
    </div>

    <!-- Independent Clipping Container (Marquee NEVER overlaps badge) -->
    <div class="relative flex-1 overflow-hidden h-5 flex items-center">
      <div class="pointer-events-none absolute left-0 top-0 bottom-0 w-3 bg-gradient-to-r from-emerald-700 to-transparent z-10"></div>
      <div class="ticker-move text-emerald-50 text-xs font-semibold whitespace-nowrap" id="ticker-content">
        लासलगाव बाजार समितीत उन्हाळ कांद्याला ₹२,४२० चा भाव • खरीप सोयाबीन हमीभाव खरेदी नोंदणी सुरू • पुणे यार्डात भाजीपाल्याची बंपर आवक • कापूस दरात तेजी: अकोला व यवतमाळ बाजारात ₹७,२५० प्रति क्विंटल • जळगाव रावेर केळीची थेट आखाती देशांत निर्यात सुरू
      </div>
    </div>
  </div>"""

for fe_path in ['src/frontend.html', 'backend/src/frontend.html']:
    if os.path.exists(fe_path):
        with open(fe_path, 'r', encoding='utf-8') as f:
            html = f.read()

        if '<link rel="icon"' not in html:
            html = html.replace('</head>', '  <link rel="icon" type="image/png" href="/icon.png">\n  <link rel="apple-touch-icon" href="/icon.png">\n</head>')

        html = html.replace(
            '<span class="text-lg sm:text-2xl">🚜</span>',
            '<img src="/icon.png" alt="KisanSetu" class="w-7 h-7 sm:w-9 sm:h-9 object-contain rounded-lg" onerror="this.outerHTML=\'<span class=\\\'text-lg sm:text-2xl\\\'>🚜</span>\'">'
        )

        t1 = html.find('<!-- Live Marquee Ticker')
        t2 = html.find('<!-- MOBILE-FIRST CLEAN RESPONSIVE HEADER -->')
        if t1 != -1 and t2 != -1:
            html = html[:t1] + new_ticker_html + "\n\n  " + html[t2:]
            print(f"Fixed ticker overlap in {fe_path}")

        with open(fe_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Updated {fe_path}")

print("Done! Zero-overlap ticker and app icon generated without any extra libraries.")
