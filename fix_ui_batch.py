import os
import re

templates_dir = r"c:\Proyectodiamantepro\DIAMANTE_PRO\app\templates"

count_updated = 0

for filename in os.listdir(templates_dir):
    if not filename.endswith(".html"):
        continue
        
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = content
    
    # 1. Navbar bg-primary -> bg-dark (Class based)
    new_content = new_content.replace('navbar-dark bg-primary', 'navbar-dark bg-dark')
    
    # 1b. Navbar with Blue Gradient Style -> bg-dark (Inline style based)
    if 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)' in new_content:
        new_content = new_content.replace('style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);"', '')
        if 'navbar-dark' in new_content and 'bg-dark' not in new_content:
             new_content = new_content.replace('navbar-dark', 'navbar-dark bg-dark')

    # 1c. Navbar with NO background class (only navbar-dark) -> add bg-dark
    if '<nav class="navbar navbar-expand-lg navbar-dark">' in new_content:
        new_content = new_content.replace('<nav class="navbar navbar-expand-lg navbar-dark">', '<nav class="navbar navbar-expand-lg navbar-dark bg-dark">')
    
    # 2. Badges (light/white box) -> bg-secondary text-white
    new_content = new_content.replace('badge bg-light text-primary', 'badge bg-secondary text-white')
    new_content = new_content.replace('badge bg-light text-dark', 'badge bg-secondary text-white')
    
    # 3. Buttons (light/white box) -> btn-outline-light
    new_content = new_content.replace('btn btn-light', 'btn btn-outline-light')
    
    # 4. Card Headers bg-primary -> bg-dark
    new_content = new_content.replace('card-header bg-primary', 'card-header bg-dark')
    
    # 5. Card bg-primary -> bg-dark
    new_content = new_content.replace('card bg-primary text-white', 'card bg-dark text-white')

    if new_content != content:
        print(f"Updating {filename}...")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        count_updated += 1
        
print(f"Total files updated: {count_updated}")
