import os
from PIL import Image, ImageDraw

# 1. Generate crisp 512x512 KisanSetu Tractor Emblem
img = Image.new("RGBA", (512, 512), (248, 250, 252, 0))
d = ImageDraw.Draw(img)
# Outer emerald border
d.ellipse([16, 16, 496, 496], fill=(16, 185, 129, 255))
d.ellipse([32, 32, 480, 480], fill=(15, 23, 42, 255))
# Golden sunrise
d.ellipse([180, 100, 332, 252], fill=(245, 158, 11, 255), outline=(251, 191, 36, 255), width=8)
# Field hills
d.chord([40, 320, 472, 550], 180, 360, fill=(34, 197, 94, 255))
d.chord([120, 350, 520, 580], 180, 360, fill=(21, 128, 61, 255))
# Rear wheel
d.ellipse([100, 320, 220, 440], fill=(51, 65, 85, 255), outline=(241, 245, 249, 255), width=12)
d.ellipse([135, 355, 185, 405], fill=(245, 158, 11, 255))
# Front wheel
d.ellipse([300, 360, 380, 440], fill=(51, 65, 85, 255), outline=(241, 245, 249, 255), width=10)
d.ellipse([325, 385, 355, 415], fill=(245, 158, 11, 255))
# Body
d.rectangle([170, 300, 340, 370], fill=(16, 185, 129, 255))
d.polygon([(160, 300), (220, 220), (280, 220), (280, 300)], fill=(5, 150, 105, 255))
d.rectangle([320, 290, 360, 370], fill=(16, 185, 129, 255))
d.rectangle([340, 240, 352, 290], fill=(203, 213, 225, 255))

for path in ['src', 'backend/src', '.']:
    if os.path.exists(path):
        img.save(os.path.join(path, 'icon.png'))
print("App icon generated successfully.")

# 2. Update api.py to serve /icon.png and use it in manifest
for api_path in ['src/api.py', 'backend/src/api.py']:
    if os.path.exists(api_path):
        with open(api_path, 'r', encoding='utf-8') as f:
            api_c = f.read()
        
        # Replace icon url with local self-hosted icon
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
        print(f"Updated {api_path}")

# 3. Update frontend.html: Fix Ticker Overlap & Insert Logo
new_ticker_html = """  <!-- Live Marquee Ticker (Isolated, Zero-Overlap) -->
  <div class="relative z-50 w-full bg-gradient-to-r from-emerald-800 via-emerald-700 to-amber-600 text-xs font-bold shadow-sm flex items-center py-1 px-2 overflow-hidden border-b border-emerald-900/30">
    <!-- Opaque Fixed Left Badge -->
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

        # Add icon links to head if missing
        if '<link rel="icon"' not in html:
            html = html.replace('</head>', '  <link rel="icon" type="image/png" href="/icon.png">\n  <link rel="apple-touch-icon" href="/icon.png">\n</head>')

        # Replace header emoji with real icon.png
        html = html.replace(
            '<span class="text-lg sm:text-2xl">🚜</span>',
            '<img src="/icon.png" alt="KisanSetu" class="w-7 h-7 sm:w-9 sm:h-9 object-contain rounded-lg" onerror="this.outerHTML=\'<span class=\\\'text-lg sm:text-2xl\\\'>🚜</span>\'">'
        )

        # Replace ticker section with clean non-overlapping version
        t1 = html.find('<!-- Live Marquee Ticker')
        t2 = html.find('<!-- MOBILE-FIRST CLEAN RESPONSIVE HEADER -->')
        if t1 != -1 and t2 != -1:
            html = html[:t1] + new_ticker_html + "\n\n  " + html[t2:]
            print(f"Fixed ticker overlap in {fe_path}")

        with open(fe_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Updated {fe_path}")

print("Done! Ticker overlap fixed and app icon is live.")
