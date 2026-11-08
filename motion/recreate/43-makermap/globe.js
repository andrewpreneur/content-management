// Segment-2 layers: orange "You're on the map" dot, pulse rings, dotted globe with maker pins, counter pill.
// Pure function of reference time T. Hooks into MM.render via window.MM_EXTRA.
(function () {
  const { S, clamp, lerp, vis, fade, path } = MM;
  const $ = (id) => document.getElementById(id);
  const D2R = Math.PI / 180;
  const PT = [-8.6, 39.4]; // the user's pin (Portugal)

  // view rotation [T, lon0, lat0] fitted per 0.1 s (density-correlation fit of land dots, r=0.90-0.93)
  const ROT = [[6.5, -9, 39], [6.75, -10, 40], [6.85, -13, 40], [6.9, -16, 40], [7.0, -25.5, 37.5], [7.1, -33.8, 35.5], [7.2, -42.9, 32.5],
    [7.3, -50, 29.5], [7.4, -55, 27.8], [7.5, -60.6, 26.6], [7.6, -63.7, 25.7], [7.7, -66.7, 25.3], [7.8, -69.3, 25.2], [7.9, -71.2, 25],
    [8.0, -71.9, 24.8], [8.1, -72.5, 24.5], [8.2, -73.5, 24.3], [8.3, -74, 24], [8.4, -74.3, 23.9], [8.5, -70.4, 24.2], [8.6, -64.7, 25.4],
    [8.7, -55.7, 27.5], [8.8, -46.9, 30.5], [8.9, -39, 33], [9.0, -33, 34.3], [9.1, -27.7, 35.2], [9.2, -23, 35.7], [9.3, -19.3, 36.3],
    [9.4, -16.9, 37], [9.5, -15, 37.5]];
  // counter keys (read off the reference)
  const CNT = [[7.12, 1580], [7.25, 1645], [7.3, 1682], [7.5, 3080], [7.7, 3336], [7.75, 3358], [7.9, 3360], [8.1, 3377], [8.3, 3389], [8.5, 3393]];

  let ctx = null, pinT = null;
  function angDist(lon1, lat1, lon2, lat2) {
    const a = Math.sin(lat1 * D2R) * Math.sin(lat2 * D2R) + Math.cos(lat1 * D2R) * Math.cos(lat2 * D2R) * Math.cos((lon1 - lon2) * D2R);
    return Math.acos(clamp(a, -1, 1)) / D2R;
  }
  // pulse wave from the user's pin: angular radius theta(T) = 110*(1-exp(-(T-7.02)/0.45)); pins pop as it passes
  const WAVE = [[7.0, 0], [7.1, 8], [7.2, 18], [7.3, 42], [7.4, 60], [7.5, 72], [7.6, 80], [7.7, 86], [7.9, 95], [8.3, 112]];
  const waveTheta = (T) => (T < 7.0 ? 0 : path(WAVE.map(([t, v]) => [t, v, 0]), T)[0]);
  // inverse of the wave: when does it reach angular distance d
  function waveTime(d) { if (d >= 111) return 8.3; for (let t = 7.0; t < 8.3; t += 0.005) if (waveTheta(t) >= d) return t; return 8.3; }
  function init() {
    const c = $('gl'); ctx = c.getContext('2d');
    pinT = PINS.map(([lo, la]) => {
      const d = angDist(lo, la, PT[0], PT[1]);
      return waveTime(d);
    });
  }

  function extra(T, st) {
    if (!ctx) init();
    // ---- user dot, halo, rings, caption (5.65 -> 6.9) ----
    const po = T < 5.66 ? 0 : 1 - Math.exp(-(T - 5.66) / 0.085);           // dot grows (first-order, tau 85 ms)
    const cyDot = 720 - 65 * S(T - 5.66, 12, 1);                             // group rises 65 px
    // globe geometry
    const tg = 1000 + 3000 * Math.exp(-Math.max(0, T - 6.532) / 0.09);       // sphere: spring to a relaxing target
    const dS = T < 6.532 ? 0 : tg * S(T - 6.532, 15.85, 0.7045);
    const gcx = 718, gcy = lerp(630, 706, S(T - 6.55, 14, 1));
    const Rd = dS / 2 * 0.988;
    const [lon0, lat0] = path(ROT, T);
    const sl = Math.sin(lat0 * D2R), cl = Math.cos(lat0 * D2R);
    const proj = (lon, lat) => {
      const cp = Math.cos(lat * D2R), sp = Math.sin(lat * D2R), dl = (lon - lon0) * D2R;
      const x = cp * Math.sin(dl), y = cl * sp - sl * cp * Math.cos(dl), mu = sl * sp + cl * cp * Math.cos(dl);
      return [gcx + Rd * x, gcy - Rd * y, mu];
    };
    // user dot: from caption layout into the globe pin
    let ux = 720, uy = cyDot, ud = 108 * po;
    if (T >= 6.5) {
      const [px, py] = proj(PT[0], PT[1]);
      const k = S(T - 6.5, 12, 1);
      ux = lerp(720, px, k); uy = lerp(655, py, k);
      ud = 20 + 88 * Math.exp(-(T - 6.5) / 0.14);
    }
    const ud_ = $('udot');
    ud_.style.visibility = po > 0.001 && T < 9.55 ? 'visible' : 'hidden';
    ud_.style.width = ud_.style.height = ud + 'px';
    ud_.style.left = (ux - ud / 2) + 'px'; ud_.style.top = (uy - ud / 2) + 'px';
    const hd = ud * 1.52;                                                    // soft pink halo (orange @22%)
    const ha = $('halo');
    ha.style.width = ha.style.height = hd + 'px';
    ha.style.left = (ux - hd / 2) + 'px'; ha.style.top = (uy - hd / 2) + 'px';
    ha.style.opacity = po * (T < 6.48 ? 1 : Math.max(0, 1 - (T - 6.48) / 0.08));
    ha.style.visibility = ud_.style.visibility;
    // ring 1 (5.70-5.95) and ring 2 (5.95-6.45)
    const ring = (el, d, a) => { el.style.width = el.style.height = d + 'px'; el.style.left = (720 - d / 2) + 'px'; el.style.top = (cyDot - d / 2) + 'px'; el.style.opacity = Math.max(0, a); el.style.visibility = a > 0.005 ? 'visible' : 'hidden'; };
    ring($('ring1'), 250 + 50 * (1 - Math.exp(-Math.max(0, T - 5.7) / 0.06)), T < 5.7 ? 0 : 0.4 * (1 - clamp((T - 5.85) / 0.15)) * clamp((T - 5.7) / 0.03));
    ring($('ring2'), 158 + 135 * (1 - Math.exp(-Math.max(0, T - 5.95) / 0.12)), T < 5.95 ? 0 : 0.85 * (1 - clamp((T - 6.3) / 0.15)));
    // caption
    const cv = vis(T, 5.87, 5.97, 6.43, 6.5);
    fade($('ymap'), cv, 12, `translate(-50%,${(17 * (1 - S(T - 5.87, 14, 1)) - 3 * clamp((T - 6.43) / 0.07)).toFixed(2)}px)`);

    // ---- sphere ----
    const sp_ = $('sphere');
    sp_.style.visibility = dS > 2 ? 'visible' : 'hidden';
    sp_.style.width = sp_.style.height = dS + 'px';
    sp_.style.left = (gcx - dS / 2) + 'px'; sp_.style.top = (gcy - dS / 2) + 'px';
    const Rv = dS / 2;
    const st2 = [[0, 251], [0.5, 250], [0.8, 246], [1.0, 240], [1.2, 232], [1.32, 228]].map(([r, L]) => `rgb(${L},${L},${L}) ${(r * Rv).toFixed(1)}px`).join(',');
    sp_.style.background = `radial-gradient(circle at 40% 36%, ${st2})`;
    const sb = T < 6.8 ? 9 * (1 - clamp((T - 6.55) / 0.25)) : 0;
    sp_.style.filter = sb > 0.05 ? `blur(${sb.toFixed(2)}px)` : 'none';

    // ---- dots + pins on canvas ----
    ctx.clearRect(0, 0, 1440, 1440);
    if (T >= 6.66 && Rd > 10) {
      const k = Rd / 494;
      const reveal = Math.max(0, (T - 6.655) * 450);                         // radial wipe from the user's pin (deg)
      const ramp = 0.55 + 0.45 * clamp((T - 6.7) / 0.5);                     // dots darken in over the first 0.5 s
      // rotation speed -> number of shutter sub-samples (180-degree shutter at 60 fps = 1/120 s)
      const [l1, a1] = path(ROT, T + 1 / 240), [l2, a2] = path(ROT, T - 1 / 240);
      const pxMove = Math.hypot(l1 - l2, a1 - a2) * D2R * Rd;
      const NS = Math.max(1, Math.min(8, Math.ceil(pxMove / 2.5)));
      const subs = [];
      for (let j = 0; j < NS; j++) {
        const tt = T + (NS === 1 ? 0 : (j / (NS - 1) - 0.5) / 120);
        const [lo0, la0] = path(ROT, tt);
        subs.push([Math.sin(la0 * D2R), Math.cos(la0 * D2R), lo0]);
      }
      for (let i = 0; i < LAND.length; i++) {
        const [lo, la] = LAND[i];
        const cp = Math.cos(la * D2R), spn = Math.sin(la * D2R);
        let a0 = ramp;
        if (reveal < 180) { const d = angDist(lo, la, PT[0], PT[1]); a0 *= clamp((reveal - d) / 15); if (a0 <= 0) continue; }
        for (const [sl_, cl_, lo0] of subs) {
          const dl = (lo - lo0) * D2R;
          const mu = sl_ * spn + cl_ * cp * Math.cos(dl);
          if (mu <= 0.02) continue;
          const x = gcx + Rd * cp * Math.sin(dl), y = gcy - Rd * (cl_ * spn - sl_ * cp * Math.cos(dl));
          const a = a0 * clamp((mu - 0.02) / 0.12) / Math.sqrt(NS);
          const w = 0.4 + 0.6 * mu, L = Math.round(245 - 172 * w);
          const r = 2.9 * (0.55 + 0.45 * mu) * k;
          ctx.fillStyle = `rgba(${L},${L},${L + 3},${a.toFixed(3)})`;
          ctx.beginPath(); ctx.arc(x, y, r, 0, 6.2832); ctx.fill();
        }
      }
      // pins pop in as the wave passes (spring w=18, z=0.5)
      for (let i = 0; i < PINS.length; i++) {
        const t0 = pinT[i]; if (T < t0) continue;
        const [lo, la, rp] = PINS[i];
        const [x, y, mu] = proj(lo, la);
        if (mu <= 0.03) continue;
        const s = S(T - t0, 18, 0.5);
        const r = 0.65 * rp * k * (0.55 + 0.45 * mu) * s;
        if (r < 0.3) continue;
        ctx.fillStyle = `rgba(226,85,42,${(0.88 * clamp((mu - 0.03) / 0.15)).toFixed(3)})`;
        ctx.beginPath(); ctx.arc(x, y, r, 0, 6.2832); ctx.fill();
      }
      // the travelling wave ring (small circle of radius theta around the user's pin)
      const th = waveTheta(T);
      if (th > 0.5 && th < 108) {
        ctx.strokeStyle = `rgba(226,85,42,${(0.42 * (1 - th / 110)).toFixed(3)})`;
        ctx.lineWidth = 5 * k; ctx.filter = "blur(1.5px)";
        const la1 = PT[1] * D2R, lo1 = PT[0] * D2R, dd = th * D2R;
        ctx.beginPath(); let pen = false;
        for (let b = 0; b <= 360; b += 2) {
          const br = b * D2R;
          const la2 = Math.asin(Math.sin(la1) * Math.cos(dd) + Math.cos(la1) * Math.sin(dd) * Math.cos(br));
          const lo2 = lo1 + Math.atan2(Math.sin(br) * Math.sin(dd) * Math.cos(la1), Math.cos(dd) - Math.sin(la1) * Math.sin(la2));
          const [x, y, mu] = proj(lo2 / D2R, la2 / D2R);
          if (mu > 0) { if (pen) ctx.lineTo(x, y); else { ctx.moveTo(x, y); pen = true; } } else pen = false;
        }
        ctx.stroke(); ctx.filter = "none";
      }
    }

    // ---- counter pill ----
    const pv = vis(T, 7.12, 7.24, 9.33, 9.4);
    const pl = $('pill');
    const ps = lerp(0.45, 1, S(T - 7.12, 20, 0.75));
    fade(pl, pv, 10, `translate(-50%,-50%) scale(${ps.toFixed(4)})`);
    const n = Math.round(MM.table(CNT, T));
    $('cnt').textContent = n.toLocaleString('en-US');
  }
  window.MM_EXTRA = extra;
})();
