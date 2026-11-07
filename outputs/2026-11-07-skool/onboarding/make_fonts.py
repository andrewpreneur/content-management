#!/usr/bin/env python3
"""Embed brand fonts from tools/fonts as base64 -> build/fonts.css (not committed, ~1 MB)."""
import base64, os
F = os.path.join(os.path.dirname(__file__), '../../../tools/fonts/')
faces = [('Inter', 'Inter-Regular.woff', 400, 'normal', 'woff'), ('Inter', 'Inter-SemiBold.woff', 600, 'normal', 'woff'),
         ('Inter', 'Inter-Bold.woff', 700, 'normal', 'woff'), ('Inter Tight', 'InterTight-ExtraBold.ttf', 800, 'normal', 'truetype'),
         ('Instrument Serif', 'InstrumentSerif-Italic.ttf', 400, 'italic', 'truetype')]
css = ''
for fam, f, w, st, fmt in faces:
    b = base64.b64encode(open(F + f, 'rb').read()).decode()
    css += f"@font-face{{font-family:'{fam}';src:url(data:font/{'woff' if fmt == 'woff' else 'ttf'};base64,{b}) format('{fmt}');font-weight:{w};font-style:{st};}}\n"
os.makedirs(os.path.join(os.path.dirname(__file__), 'build'), exist_ok=True)
open(os.path.join(os.path.dirname(__file__), 'build/fonts.css'), 'w').write(css)
