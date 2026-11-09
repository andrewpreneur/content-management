#!/usr/bin/env python3
"""Audio mix for a VSL: original voice + ducked ambient music + soft SFX at the overlay's cue times.
python3 mix.py <base.mp4> <music.mp3> <cues.json> <dur> <out.wav>   -> master -14 LUFS, TP <= -1.5 dB (two-pass loudnorm)."""
import json, subprocess, sys, re, os
base, music, cues, dur, out = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5]
SFX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../vendor/motion-graphics/skills/sound-effects/sfx/')
KIT = {'whoosh': ('kit/whoosh.ogg', 0.22), 'pop': ('kit/pop.ogg', 0.30), 'click': ('click/kenney-interface-click-001.ogg', 0.28),
       'tick': ('kit/tick.ogg', 0.28), 'ding': ('ding/kenney-interface-confirmation-001.ogg', 0.25), 'type': ('click/kenney-interface-tick-001.ogg', 0.10),
       'riser': ('kit/riser.ogg', 0.12)}
C = sorted(json.load(open(cues)), key=lambda c: c['t'])
keep, last = [], {}
for c in C:  # de-duplicate same-kind cues closer than 0.12 s
    if c['t'] - last.get(c['k'], -9) >= 0.12 and c['t'] < dur: keep.append(c); last[c['k']] = c['t']
ins = ['-i', base, '-i', music]; fl = []
for i, c in enumerate(keep):
    f, v = KIT[c['k']]; ins += ['-i', SFX + f]; d = int(c['t'] * 1000)
    fl.append(f'[{i+2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={d}|{d}[s{i}]')
fl.append(f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={dur},asplit=2[v][sc]')
fl.append(f'[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{dur},afade=t=in:d=1.5,afade=t=out:st={dur-2.5}:d=2.5,volume=0.32[m0]')
fl.append('[m0][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[m]')
fl.append(f'[v][m]' + ''.join(f'[s{i}]' for i in range(len(keep))) + f'amix=inputs={2+len(keep)}:normalize=0:duration=first,atrim=0:{dur}[mix]')
fc = ';'.join(fl)
def run(extra, o):
    return subprocess.run(['ffmpeg', '-v', 'info', '-y', *ins, '-filter_complex', fc + ';[mix]' + extra + '[a]', '-map', '[a]', '-ar', '48000', *o], capture_output=True, text=True)
r = run('loudnorm=I=-14:TP=-2.2:LRA=11:print_format=json', ['-f', 'null', '-'])
m = json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr)[-1])
r = run(f"loudnorm=I=-14:TP=-2.2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,alimiter=limit=0.72:attack=3:release=60:level=false", [out])
if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
print('sfx cues', len(keep), 'input', m['input_i'])
