import os
import glob
import re

for js_file in glob.glob('f:/learnbydoingwithsteven/cag_10/*/frontend/src/App.js'):
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = re.sub(r'elevation=(\d+)', r'elevation={\1}', content)
    if new_content != content:
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed {js_file}')
