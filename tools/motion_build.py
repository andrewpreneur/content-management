#!/usr/bin/env python3
"""Build motion clips that share code: expands `//@include file.js` lines (path relative to the clip) and then runs the
vendored motion-broll build.py. Usage: python3 tools/motion_build.py motion/dist motion/clips/a.html [b.html ...]"""
import re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / 'vendor/motion-graphics/skills/motion-broll/engine/build.py'


def expand(p):
    return re.sub(r'^\s*//@include\s+(\S+)\s*$', lambda m: (p.parent / m.group(1)).read_text(), p.read_text(), flags=re.M)


if __name__ == '__main__':
    out = sys.argv[1]
    with tempfile.TemporaryDirectory() as td:
        srcs = []
        for s in sys.argv[2:]:
            p = Path(s).resolve(); t = Path(td) / p.name; t.write_text(expand(p)); srcs.append(str(t))
        subprocess.run([sys.executable, str(BUILD), out, *srcs], check=True)
