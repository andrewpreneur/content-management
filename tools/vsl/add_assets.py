#!/usr/bin/env python3
"""Merge 'name id name id ...' pairs into outputs/2026-11-07-vsl-a/assets.json"""
import json, sys
p = 'outputs/2026-11-07-vsl-a/assets.json'; a = json.load(open(p)); x = sys.argv[1:]
for k, v in zip(x[::2], x[1::2]): a[k] = '/_blob/' + v
json.dump(a, open(p, 'w'), indent=1); print(len(a))
