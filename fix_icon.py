from PIL import Image, ImageDraw
import os

# Create a 512x512 crisp green KisanSetu tractor/sprout icon
img = Image.new("RGBA", (512, 512), (21, 128, 61, 255))
d = ImageDraw.Draw(img)
# Circular outer border
d.ellipse([20, 20, 492, 492], fill=(22, 163, 74, 255), outline=(245, 158, 11, 255), width=16)
# Inner accent circle
d.ellipse([60, 60, 452, 452], fill=(21, 128, 61, 255))
# Center badge text / shape
d.ellipse([160, 160, 352, 352], fill=(245, 158, 11, 255))
d.ellipse([180, 180, 332, 332], fill=(255, 255, 255, 255))

for path in ["src", "backend/src"]:
    if os.path.exists(path):
        img.save(os.path.join(path, "icon.png"))
        print(f"Saved icon to {path}/icon.png")

# Update manifest in api.py to use the local self-hosted icon
for api_path in ["src/api.py", "backend/src/api.py"]:
    if os.path.exists(api_path):
        with open(api_path, "r", encoding="utf-8") as f:
            c = f.read()
        c = c.replace(
            "https://cdn-icons-png.flaticon.com/512/2990/2990479.png",
            "/icon.png"
        )
        if "@app.get(\"/icon.png\")" not in c:
            c += """

@app.get("/icon.png")
def get_app_icon():
    from fastapi.responses import FileResponse
    icon_file = os.path.join(current_dir, "icon.png")
    return FileResponse(icon_file, media_type="image/png")
"""
        with open(api_path, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"Updated {api_path} with /icon.png endpoint")

print("Done! Icon is ready.")
