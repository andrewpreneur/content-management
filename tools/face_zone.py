#!/usr/bin/env python3
"""Measure where the speaker's head is across a video so graphics never cover the face.
Usage: python3 tools/face_zone.py video.mp4 [every_n_frames=10]
Prints JSON {W, H, head:[x0,y0,x1,y1], frames}. head = union over sampled frames of a box around nose/eyes/ears
(Keypoint R-CNN), widened to cover hair and chin. Keep every text/graphic outside head + 40px.
Needs torch + torchvision (pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu)."""
import json, subprocess, sys
import numpy as np, torch
from torchvision.models.detection import keypointrcnn_resnet50_fpn, KeypointRCNN_ResNet50_FPN_Weights


def main():
    src = sys.argv[1]; every = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    W, H = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip().split(','))
    s = 640 / max(W, H); w, h = int(W * s) // 2 * 2, int(H * s) // 2 * 2
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-vf', f"select='not(mod(n,{every}))',scale={w}:{h}", '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    m = keypointrcnn_resnet50_fpn(weights=KeypointRCNN_ResNet50_FPN_Weights.DEFAULT).eval(); torch.set_num_threads(4)
    boxes = []
    while True:
        b = p.stdout.read(w * h * 3)
        if len(b) < w * h * 3: break
        img = torch.from_numpy(np.frombuffer(b, np.uint8).reshape(h, w, 3).copy()).permute(2, 0, 1).float() / 255
        with torch.no_grad(): o = m([img])[0]
        if not len(o['scores']) or o['scores'][0] < 0.8: continue
        k = o['keypoints'][0][:5, :2].numpy() / s  # nose, l/r eye, l/r ear
        x0, x1 = k[:, 0].min(), k[:, 0].max(); cx, fw = (x0 + x1) / 2, max(x1 - x0, 1)
        ey, ny = k[1:3, 1].mean(), k[0, 1]
        boxes.append([cx - 0.85 * fw, ey - 1.4 * fw, cx + 0.85 * fw, ny + 0.95 * fw])
    a = np.array(boxes)
    head = [max(0, a[:, 0].min()), max(0, a[:, 1].min()), min(W, a[:, 2].max()), min(H, a[:, 3].max())]
    print(json.dumps(dict(W=W, H=H, head=[round(float(v)) for v in head], frames=len(a))))


if __name__ == '__main__':
    main()
