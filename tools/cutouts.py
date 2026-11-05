#!/usr/bin/env python3
"""People cut-outs for 'words behind the speaker' (run with the torch venv).
  /home/user/work/dfenv/bin/python tools/cutouts.py FRAMES_DIR 12,14,16,...   → FRAMES_DIR/cNNNN.webp (2560 wide, alpha = people)
DeepLabV3-MobileNetV3 person class, soft edge. ~1 s/frame on 4 CPUs, so only the frames that need it."""
import sys, os, torch, numpy as np
from PIL import Image, ImageFilter
from torchvision.models.segmentation import deeplabv3_mobilenet_v3_large, DeepLabV3_MobileNet_V3_Large_Weights
d, nums = sys.argv[1], [int(x) for x in sys.argv[2].split(',') if x]
w = DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT; m = deeplabv3_mobilenet_v3_large(weights=w).eval(); tf = w.transforms(); torch.set_num_threads(4)
for n in nums:
    out = f'{d}/c{n:04d}.webp'
    if os.path.exists(out): continue
    im = Image.open(f'{d}/f{n:04d}.jpg').convert('RGB'); small = im.resize((1280, 720))
    with torch.no_grad():
        p = m(tf(small).unsqueeze(0))['out'][0].softmax(0)[15].numpy()
    a = Image.fromarray((np.clip((p - 0.35) / 0.3, 0, 1) * 255).astype(np.uint8)).resize((2560, 1440), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
    big = im.resize((2560, 1440), Image.LANCZOS); big.putalpha(a); big.save(out, 'WEBP', quality=86)
print('cutouts', len(nums))
