// SaaSSuite motion primitives — every curve measured from the reference recreations (motion/recreate/*/notes.md).
// All functions are pure functions of time so a page can expose window.render(t) and be shot frame by frame.
const SS = (() => {
  const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, p) => a + (b - a) * p;
  const ease = {
    outCubic: x => 1 - Math.pow(1 - cl(x), 3),
    outQuart: x => 1 - Math.pow(1 - cl(x), 4),
    outExpo: x => (x = cl(x)) >= 1 ? 1 : 1 - Math.pow(2, -10 * x),
    inOutCubic: x => (x = cl(x)) < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
    inOutSine: x => -(Math.cos(Math.PI * cl(x)) - 1) / 2,
    bezier: (x1, y1, x2, y2) => x => { x = cl(x); let t = x; for (let i = 0; i < 8; i++) { const cx = 3 * x1 * t * (1 - t) ** 2 + 3 * x2 * t * t * (1 - t) + t ** 3 - x; const d = 3 * x1 * (1 - t) ** 2 + 6 * (x2 - x1) * t * (1 - t) + 3 * (1 - x2) * t * t; if (Math.abs(d) < 1e-6) break; t = cl(t - cx / d); } return 3 * y1 * t * (1 - t) ** 2 + 3 * y2 * t * t * (1 - t) + t ** 3; },
  };
  // Damped spring progress 0->1 (mass 1, stiffness w^2, damping 2*z*w). tau = seconds since start.
  function spring(tau, w = 16, z = 0.7) {
    if (tau <= 0) return 0;
    if (z < 1) { const wd = w * Math.sqrt(1 - z * z); return 1 - Math.exp(-z * w * tau) * (Math.cos(wd * tau) + (z * w / wd) * Math.sin(wd * tau)); }
    return 1 - Math.exp(-w * tau) * (1 + w * tau);
  }
  // Spring displacement from x0 with initial velocity v0 (px, px/s) -> current offset (ClimbX letter rise).
  function springOffset(tau, x0, v0, w, z) {
    if (tau <= 0) return x0; const wd = w * Math.sqrt(1 - z * z);
    return Math.exp(-z * w * tau) * (x0 * Math.cos(wd * tau) + ((v0 + z * w * x0) / wd) * Math.sin(wd * tau));
  }
  // 1. Letter spring-rise headline (ClimbX). Returns per-letter {y, rot, blur, op}.
  function letterRise(t, t0, i, o = {}) {
    const { stagger = 0.0453, x0 = 73.5, v0 = -628, w = 15.9, z = 0.47 } = o; const tau = t - t0 - i * stagger;
    const y = springOffset(tau, x0, v0, w, z), dt = 1 / 120, v = (springOffset(tau + dt, x0, v0, w, z) - y) / dt;
    return { y, rot: 0.18 * y, blur: tau <= 0 ? 3.5 : Math.min(3.5, Math.abs(v) / 260), op: cl(tau / 0.07) };
  }
  // 2. Word blur-rise (soft headline / captions in). 0.55s outQuart, 40px, 10px blur, 0.11s stagger.
  function wordRise(t, t0, i, o = {}) { const { stagger = 0.11, dur = 0.55, dy = 40, blur = 10 } = o; const p = ease.outQuart((t - t0 - i * stagger) / dur); return { y: (1 - p) * dy, blur: (1 - p) * blur, op: p }; }
  // 3. Card slide-in on a spring (ClimbX): from dx px, w 23.8, z 0.78, x-motion-blur 0.45*|v|/30.
  function cardSlide(t, t0, dx = 358, w = 23.8, z = 0.78) { const tau = t - t0; const p = spring(tau, w, z), p2 = spring(tau + 1 / 120, w, z); const v = (p2 - p) * 120 * dx; return { x: (1 - p) * dx, blurX: 0.45 * Math.abs(v) / 30, op: cl(tau / 0.1) }; }
  // 4. Stamp slam (pills, icons, logos): scale 2.25 -> 0.67 (6.5f inOutSine) then spring overshoot to ~1.24, settle.
  function stamp(t, t0, fps = 30) { const f = (t - t0) * fps; if (f < 0) return { s: 2.25, rot: -24, op: 0 }; if (f < 6.5) { const p = ease.inOutSine(f / 6.5); return { s: lerp(2.25, 0.67, p), rot: lerp(-24, 6, p), op: cl(f / 1.6) }; } return { s: 1 - 0.33 * springOffset((f - 6.5) / fps, 1, 0, 11.5, 0.3), rot: 6 * Math.exp(-(f - 6.5) / 8), op: 1 }; }
  // 5. Word slam (no letter split): scale 1 + springOffset(1.25, w15.4, z0.48), blur 12*|s-1| (max 14).
  function wordSlam(t, t0) { const s = 1 + springOffset(t - t0, 1.25, 0, 15.4, 0.48); return { s, blur: Math.min(14, 12 * Math.abs(s - 1)), op: cl((t - t0) * 30 / 1.6) }; }
  // 6. Morph (MakerMap): animate a single box between rects with independent w/h springs; radius pill = h/2.
  function morph(t, t0, from, to, o = {}) { const { ww = 16.4, wz = 0.59, hw = 16.0, hz = 0.78, delayH = 0 } = o; const pw = spring(t - t0, ww, wz), ph = spring(t - t0 - delayH, hw, hz); const w = lerp(from.w, to.w, pw), h = lerp(from.h, to.h, ph); const cx = lerp(from.cx, to.cx, pw), cy = lerp(from.cy, to.cy, ph); return { w, h, x: cx - w / 2, y: cy - h / 2, r: to.r == null ? h / 2 : lerp(from.r ?? from.h / 2, to.r, spring(t - t0, 24, 1)) }; }
  // Spring toward a relaxing target (button -> input expand-then-settle).
  function relaxTo(t, t0, from, final, kick = 186, decay = 0.161, w = 16.7, z = 0.625) { const tau = t - t0; return lerp(from, final + kick * Math.exp(-Math.max(0, tau) / decay), spring(tau, w, z)); }
  // 7. Blur-dissolve swap: old content out (0.08s, blur 0->11), new in when the shape spring passes 80%.
  function dissolveOut(t, t0, dur = 0.08) { const p = cl((t - t0) / dur); return { op: 1 - p, blur: 11 * p }; }
  // 8. Press / hover / cursor squish.
  function press(t, t0) { const tau = t - t0; if (tau < 0) return 1; if (tau < 0.1) return lerp(1, 0.954, tau / 0.1); return lerp(0.954, 1, spring(tau - 0.1, 22, 0.85)); }
  function cursorSquish(t, t0) { const tau = t - t0; if (tau < 0) return 1; if (tau < 0.06) return lerp(1, 0.85, tau / 0.06); return lerp(0.85, 1, cl((tau - 0.06) / 0.1)); }
  // 9. Typing (Tessel): ~30 chars/s at 30fps; new char born in accent, fades to ink over 5 frames.
  function typing(t, t0, text, cps = 30) { const n = Math.max(0, Math.min(text.length, Math.floor((t - t0) * cps))); return { shown: text.slice(0, n), n, ageOf: i => (t - t0) * cps - (i + 1) }; }
  // 10. Text blur-in sweep (CodePilot): each char sharpens from 10px blur over 0.6s; sweep 1230 px/s left->right.
  function sweepChar(t, t0, xPx, o = {}) { const { speed = 1230, dur = 0.6 } = o; const p = ease.outCubic((t - t0 - xPx / speed) / dur); return { op: p, blur: 10 * (1 - p) }; }
  // 11. Beat pulse (ClimbX): every beat the scene scales 1 + 0.0095*e^(-dt/0.085).
  function beatPulse(t, bpm = 90, amp = 0.0095) { const b = 60 / bpm; const dt = ((t % b) + b) % b; return 1 + amp * Math.exp(-dt / 0.085); }
  // 12. Bar fill + count-up: width = final*(1-e^(-16.9 t)), rows 0.133s apart.
  function barFill(t, t0, row = 0) { return 1 - Math.exp(-16.9 * Math.max(0, t - t0 - row * 0.133)); }
  // 13. Colour wipe from a click (Tessel): diameter = 146 + 17*1.75^(frame-f0).
  function clickWipe(t, t0, fps = 30) { const f = (t - t0) * fps; return f < 0 ? 0 : 146 + 17 * Math.pow(1.75, f); }
  // 14. Big headline blurred -> sharp settle (Tessel): op 0.07s, blur 18*(1-u)^2 over 0.10s, scale 1.07 -> 1 over 0.2s.
  function bigSettle(t, t0) { const u = cl((t - t0) / 0.10); return { op: cl((t - t0) / 0.07), blur: 18 * (1 - u) ** 2, s: lerp(1.07, 1, ease.outCubic((t - t0) / 0.2)) }; }
  // 15. Keynote 3D camera on UI (CodePilot): over 0.696s bezier(.626,.279,.251,.907): scale 1->0.81, rotY -10.76deg, rotX 3.7deg; then +4.7deg drift over 3.3s.
  function keynoteCam(t, t0) { const p = ease.bezier(0.626, 0.279, 0.251, 0.907)((t - t0) / 0.696); const drift = 4.7 * cl((t - t0 - 0.696) / 3.3); return { s: lerp(1, 0.81, p), ry: lerp(0, -10.76, p) + drift, rx: lerp(0, 3.7, p), persp: 4732 }; }
  return { cl, lerp, ease, spring, springOffset, letterRise, wordRise, cardSlide, stamp, wordSlam, morph, relaxTo, dissolveOut, press, cursorSquish, typing, sweepChar, beatPulse, barFill, clickWipe, bigSettle, keynoteCam };
})();
if (typeof module !== 'undefined') module.exports = SS;
