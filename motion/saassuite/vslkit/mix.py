#!/usr/bin/env python3
"""mix.py WORKDIR DURATION -> WORKDIR/mix.wav (voice + ducked music + SFX cues, -14 LUFS, TP <= -1.5 dB). Cached if inputs unchanged."""
import json, os, subprocess, sys
D, dur = sys.argv[1], float(sys.argv[2])
SFX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../vendor/motion-graphics/skills/sound-effects/sfx/')
M = {'whoosh': 'transition/fs-786514-swoosh-v2.ogg', 'swish': 'kit/whoosh.ogg', 'pop': 'kit/pop.ogg', 'click': 'kit/click.ogg',
     'ding': 'ding/kenney-interface-confirmation-001.ogg', 'tick': 'kit/tick.ogg', 'type': 'typing/fs-416777-digital-typing-wav.ogg',
     'blip': 'ui-blip/kenney-ui-rollover2.ogg', 'riser': 'riser/fs-685256-riser-sound-effect-short-wav.ogg', 'drop': 'pop/kenney-interface-drop-002.ogg'}
out = f'{D}/mix.wav'
if os.path.exists(out) and os.path.getmtime(out) > max(os.path.getmtime(f'{D}/{f}') for f in ('cues.json', 'music.mp3', 'voice.wav')): sys.exit(0)
cues = json.load(open(f'{D}/cues.json'))
inp = ['-i', f'{D}/voice.wav', '-i', f'{D}/music.mp3']; fl = []
for k, (t, kind, g) in enumerate(cues):
    inp += ['-i', SFX + M[kind]]
    trim = ',atrim=0:1.2' if kind == 'type' else ''
    fl.append(f'[{k+2}:a]aformat=sample_rates=48000:channel_layouts=stereo{trim},volume={g-12}dB,adelay={int(t*1000)}|{int(t*1000)}[s{k}]')
fe = dur - 2.5
fl.append(f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,apad,atrim=0:{dur},asplit=2[v][sc]')
fl.append(f'[1:a]aformat=sample_rates=48000:channel_layouts=stereo,apad,atrim=0:{dur},volume=-17dB,afade=t=in:d=1.5,afade=t=out:st={fe}:d=2.5[m0]')
fl.append('[m0][sc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=500[m]')
mixin = '[v][m]' + ''.join(f'[s{k}]' for k in range(len(cues)))
fl.append(f'{mixin}amix=inputs={len(cues)+2}:normalize=0:duration=first[mx]')
tmp = f'{D}/premix.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inp, '-filter_complex', ';'.join(fl), '-map', '[mx]', '-t', str(dur), tmp], check=True)
r = subprocess.run(['ffmpeg', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
af = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', af, '-ar', '48000', out], check=True)
os.remove(tmp)
