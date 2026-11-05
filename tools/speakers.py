#!/usr/bin/env python3
"""Who is where, and who is talking when — for auto-framing podcast clips.

Run with the DeepFilterNet/torch venv (needs torch + torchvision):
  /home/user/work/dfenv/bin/python tools/speakers.py VIDEO --start S --dur D --words WORDS.json OUT.json
WORDS.json: [[word, start, end], ...] clip-relative (from tools/clip_bank.py).

1. People: Keypoint R-CNN (torchvision, COCO) on ~8 frames → each seated person's nose/eyes/ears in 4K pixels, a face size,
   tracked across samples by x position.
2. Talking: WHEN the voice changes comes from the audio — an ECAPA speaker embedding (speechbrain/spkrec-ecapa-voxceleb) per
   word (1.5 s window), clustered (cosine distance 0.8; same voice ≈ 0.5, different voice ≈ 1.0 on Pod3). WHO each voice is comes
   from the video — mouth-box frame differences at 10 fps minus a forehead box, normalised per person, summed over that voice's
   words; each voice goes to the person whose mouth moves most while it speaks. Segments shorter than 1.0 s are merged.
OUT.json: {"W":3840,"H":2160,"people":[{"id":0,"x":..,"y":..,"face":..,"box":[x0,y0,x1,y1]}],
           "segments":[[t0,t1,id],...],"main":id,"share":{id: fraction}}
Check by eye before trusting it on a new set-up (a face strip at a few timestamps).
"""
import argparse, json, subprocess
import numpy as np, torch
from torchvision.models.detection import keypointrcnn_resnet50_fpn, KeypointRCNN_ResNet50_FPN_Weights


def frames(video, t0, dur, fps, w, h, gray):
    pix = 'gray' if gray else 'rgb24'
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t0), '-t', str(dur), '-i', video, '-vf', f'fps={fps},scale={w}:{h}',
                          '-pix_fmt', pix, '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    c = 1 if gray else 3
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, c) if not gray else np.frombuffer(raw, np.uint8).reshape(-1, h, w)


def people(video, t0, dur, W, H):
    wts = KeypointRCNN_ResNet50_FPN_Weights.DEFAULT; m = keypointrcnn_resnet50_fpn(weights=wts).eval()
    n = 8; F = frames(video, t0, dur, n / max(dur, 1), 1280, 720, False)[:n]
    sx, sy = W / 1280, H / 720; dets = []
    with torch.no_grad():
        for f in F:
            o = m([torch.from_numpy(f.copy()).permute(2, 0, 1).float() / 255])[0]
            for b, s, k in zip(o['boxes'], o['scores'], o['keypoints']):
                if s < 0.85: continue
                k = k.numpy(); b = b.numpy()
                nose, le, re_, lea, rea = k[0], k[1], k[2], k[3], k[4]
                face = max(abs(lea[0] - rea[0]), abs(le[0] - re_[0]) * 2.2, (b[2] - b[0]) * 0.22)
                dets.append(dict(x=nose[0] * sx, y=nose[1] * sy, face=face * sx, box=[b[0] * sx, b[1] * sy, b[2] * sx, b[3] * sy]))
    dets.sort(key=lambda d: d['x']); groups = []
    for d in dets:  # cluster by nose x (people sit still)
        if groups and abs(d['x'] - np.median([g['x'] for g in groups[-1]])) < 0.6 * d['face'] + 60: groups[-1].append(d)
        else: groups.append([d])
    out = []
    for g in groups:
        if len(g) < max(2, n // 3): continue  # seen in too few samples → passer-by / false hit
        out.append(dict(x=float(np.median([d['x'] for d in g])), y=float(np.median([d['y'] for d in g])),
                        face=float(np.median([d['face'] for d in g])), box=[float(np.median([d['box'][i] for d in g])) for i in range(4)]))
    for i, p in enumerate(out): p['id'] = i
    return out


def talking(video, t0, dur, W, H, P, words):
    fps, w, h = 10, 960, 540; F = frames(video, t0, dur, fps, w, h, True).astype(np.float32)
    D = np.abs(np.diff(F, axis=0)); s = w / W; sig = []
    for p in P:
        fw = p['face'] * s; cx, cy = p['x'] * s, p['y'] * s
        mb = (int(cx - 0.45 * fw), int(cx + 0.45 * fw), int(cy + 0.15 * fw), int(cy + 0.75 * fw))   # mouth + jaw
        fb = (int(cx - 0.45 * fw), int(cx + 0.45 * fw), int(cy - 0.75 * fw), int(cy - 0.30 * fw))   # forehead
        clip = lambda b: (max(0, b[0]), min(w, b[1]), max(0, b[2]), min(h, b[3]))
        mb, fb = clip(mb), clip(fb)
        m = D[:, mb[2]:mb[3], mb[0]:mb[1]].mean((1, 2)); f = D[:, fb[2]:fb[3], fb[0]:fb[1]].mean((1, 2))
        v = m - 0.8 * f; v = (v - np.median(v)) / (np.percentile(v, 90) - np.median(v) + 1e-6)
        sig.append(v)
    sig = np.array(sig); tt = (np.arange(sig.shape[1]) + 1) / fps
    # voices from audio
    import io, soundfile as sf
    from speechbrain.inference.speaker import EncoderClassifier
    from scipy.cluster.hierarchy import linkage, fcluster
    enc = EncoderClassifier.from_hparams(source='speechbrain/spkrec-ecapa-voxceleb', savedir='/home/user/work/remodel/ecapa', run_opts={'device': 'cpu'})
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t0), '-t', str(dur), '-i', video, '-ac', '1', '-ar', '16000', '-f', 'wav', '-'],
                         capture_output=True, check=True).stdout
    a, sr = sf.read(io.BytesIO(raw), dtype='float32'); E = []
    with torch.no_grad():
        for wd in words:
            c = (wd[1] + wd[2]) / 2; x0 = max(0, c - 0.75); x1 = min(len(a) / sr, c + 0.75)
            E.append(enc.encode_batch(torch.from_numpy(a[int(x0 * sr):int(x1 * sr)]).unsqueeze(0)).squeeze().numpy())
    E = np.array(E); E /= np.linalg.norm(E, axis=1, keepdims=True)
    voice = fcluster(linkage(E, 'average', metric='cosine'), 0.8, 'distance') if len(words) > 1 else np.array([1])
    # voice -> person: whose mouth moves most while that voice talks (each person used once while possible)
    score = {}
    for v in set(voice):
        ks = [(tt >= wd[1]) & (tt <= max(wd[2], wd[1] + 0.15)) for wd, vv in zip(words, voice) if vv == v]
        k = np.any(ks, axis=0) if ks else np.zeros_like(tt, bool)
        score[v] = sig[:, k].mean(1) if k.any() else np.zeros(len(P))
    order = sorted(score, key=lambda v: -(voice == v).sum()); taken, vmap = set(), {}
    for v in order:
        ranked = [int(i) for i in np.argsort(-score[v])]
        vmap[v] = next((i for i in ranked if i not in taken), ranked[0]); taken.add(vmap[v])
    sm = [vmap[v] for v in voice]
    seg = []
    for wd, l in zip(words, sm):
        if seg and seg[-1][2] == l: seg[-1][1] = wd[2]
        else: seg.append([wd[1], wd[2], l])
    merged = []  # drop segments shorter than 1 s into the previous one
    for sgm in seg:
        if merged and sgm[1] - sgm[0] < 1.0: merged[-1][1] = sgm[1]
        elif merged and merged[-1][2] == sgm[2]: merged[-1][1] = sgm[1]
        else: merged.append(sgm)
    if merged: merged[0][0] = 0.0
    for a, b in zip(merged, merged[1:]): a[1] = b[0]
    return [[round(a, 2), round(b, 2), int(l)] for a, b, l in merged]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('out')
    ap.add_argument('--start', type=float, required=True); ap.add_argument('--dur', type=float, required=True); ap.add_argument('--words', required=True)
    a = ap.parse_args(); torch.set_num_threads(4)
    W, H = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', a.video],
                                   capture_output=True, text=True).stdout.strip().split(',')[:2])
    words = json.load(open(a.words)); P = people(a.video, a.start, a.dur, W, H)
    S = talking(a.video, a.start, a.dur, W, H, P, words) if len(P) > 1 else [[0.0, a.dur, 0]]
    share = {}
    for s0, s1, l in S: share[l] = share.get(l, 0) + s1 - s0
    tot = sum(share.values()) or 1
    out = dict(W=W, H=H, people=P, segments=S, main=max(share, key=share.get), share={k: round(v / tot, 2) for k, v in share.items()})
    json.dump(out, open(a.out, 'w'), indent=1); print(json.dumps({k: out[k] for k in ('main', 'share', 'segments')}))


if __name__ == '__main__':
    main()
