import os

meta_tag = '  <meta name="google-adsense-account" content="ca-pub-5030249027466076">\n'

for fe_path in ['src/frontend.html', 'backend/src/frontend.html']:
    if os.path.exists(fe_path):
        with open(fe_path, 'r', encoding='utf-8') as f:
            html = f.read()

        if 'ca-pub-5030249027466076' not in html:
            html = html.replace('<head>', '<head>\n' + meta_tag)
            with open(fe_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Added AdSense meta tag to {fe_path}")
        else:
            print("AdSense meta tag already present.")

print("Done! Ready to push.")
