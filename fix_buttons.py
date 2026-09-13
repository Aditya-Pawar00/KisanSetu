import os

for path in ['src/frontend.html', 'backend/src/frontend.html']:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()

        # Make the broadcast button visible on mobile
        c = c.replace('class="hidden sm:flex px-2.5 py-1.5', 'class="flex px-2 sm:px-2.5 py-1 sm:py-1.5')
        c = c.replace('class="hidden sm:flex', 'class="flex px-2 sm:px-2.5 py-1 sm:py-1.5')

        # Make both button labels compact and visible
        c = c.replace('class="hidden xs:inline sm:inline"', 'class="inline"')
        c = c.replace('id="btn-broadcast-txt">📡 लिलाव नोंदवा', 'id="btn-broadcast-txt">📡 लिलाव')
        c = c.replace('id="btn-report-txt" class="inline">शेतकरी भाव', 'id="btn-report-txt" class="inline">भाव')
        c = c.replace('id="btn-report-txt">भाव नोंदवा', 'id="btn-report-txt">भाव')

        # Language toggle sync
        c = c.replace(
            "document.getElementById('btn-broadcast-txt').innerText = isMr ? '📡 लिलाव नोंदवा' : '📡 Broadcast';",
            "document.getElementById('btn-broadcast-txt').innerText = isMr ? '📡 लिलाव' : '📡 Auction';"
        )
        c = c.replace(
            "document.getElementById('btn-report-txt').innerText = isMr ? 'भाव नोंदवा' : 'Submit Rate';",
            "document.getElementById('btn-report-txt').innerText = isMr ? '✍️ भाव' : '✍️ Rate';"
        )

        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"Updated {path}: Both buttons are now visible on mobile!")

print("Done! Both action buttons are now restored.")
